
import json
import sys
from pathlib import Path

from sqlalchemy import inspect, text

from app.db.session import engine


BASE_DIR = Path(__file__).resolve().parent
PREVIEW_FILE = BASE_DIR / "image_migration_preview.json"
COPY_REPORT_FILE = BASE_DIR / "image_copy_report.json"
RESULT_FILE = BASE_DIR / "image_database_migration_result.json"

TABLES = {
    "products": ["image"],
    "categories": ["image_url"],
    "recipes": ["image"],
    "recipe_categories": ["image_url"],
    "home_category_cards": ["image_url"],
}


def load_json(path):
    if not path.is_file():
        raise RuntimeError(f"Required file missing: {path.name}")

    return json.loads(path.read_text(encoding="utf-8"))


def replace_urls(obj, mapping):
    """Replace matching URL strings recursively in homepage JSON."""
    changed = 0

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and value in mapping:
                obj[key] = mapping[value]
                changed += 1
            else:
                count = replace_urls(value, mapping)
                changed += count

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, str) and value in mapping:
                obj[index] = mapping[value]
                changed += 1
            else:
                count = replace_urls(value, mapping)
                changed += count

    return changed


def migrate():
    preview = load_json(PREVIEW_FILE)
    copy_report = load_json(COPY_REPORT_FILE)

    mapping = preview.get("mapping", {})

    if not mapping:
        raise RuntimeError("No image URL mappings found.")

    if preview.get("missing_references") != 0:
        raise RuntimeError("Preview contains missing images.")

    if copy_report.get("failed") != 0:
        raise RuntimeError("Some RustFS images failed to copy.")

    if copy_report.get("copied_and_verified") != len(mapping):
        raise RuntimeError("Not all copied images were verified.")

    if len(copy_report.get("results", [])) != len(mapping):
        raise RuntimeError("Copy report is incomplete.")

    for item in copy_report["results"]:
        if not item.get("verified"):
            raise RuntimeError("An image is not verified.")

        if mapping.get(item["old_url"]) != item["new_url"]:
            raise RuntimeError("Copy report does not match preview mapping.")

    if "--apply" not in sys.argv:
        print("DRY RUN ONLY")
        print("Unique URL mappings:", len(mapping))
        print("Database changes: 0")
        print("To apply, run: python .\\apply_image_url_migration.py --apply")
        return

    inspector = inspect(engine)

    table_changes = {}
    homepage_changes = 0

    # All database changes happen in one transaction.
    with engine.begin() as conn:

        for table, image_columns in TABLES.items():

            if not inspector.has_table(table):
                continue

            columns = {
                column["name"]
                for column in inspector.get_columns(table)
            }

            for column in image_columns:
                if column not in columns:
                    continue

                total = 0

                # Only update rows whose current value exactly matches
                # a URL in the verified preview mapping.
                for old_url, new_url in mapping.items():
                    sql = text(
                        f"UPDATE `{table}` "
                        f"SET `{column}` = :new_url "
                        f"WHERE `{column}` = :old_url"
                    )

                    result = conn.execute(
                        sql,
                        {
                            "new_url": new_url,
                            "old_url": old_url,
                        },
                    )

                    total += result.rowcount or 0

                table_changes[f"{table}.{column}"] = total

        # Update image references stored inside homepage_config JSON.
        if inspector.has_table("homepage_config"):
            rows = conn.execute(
                text("SELECT id, config_json FROM homepage_config")
            ).mappings().all()

            for row in rows:
                config = row["config_json"]

                if isinstance(config, str):
                    config = json.loads(config)

                changed = replace_urls(config, mapping)

                if changed:
                    conn.execute(
                        text(
                            "UPDATE homepage_config "
                            "SET config_json = :config "
                            "WHERE id = :id"
                        ),
                        {
                            "config": json.dumps(
                                config,
                                ensure_ascii=False,
                            ),
                            "id": row["id"],
                        },
                    )

                    homepage_changes += changed

    result = {
        "database_updated": True,
        "unique_url_mappings": len(mapping),
        "table_changes": table_changes,
        "homepage_config_image_references_changed": homepage_changes,
        "old_images_deleted": False,
    }

    RESULT_FILE.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("\n========== DATABASE MIGRATION RESULT ==========")
    print(json.dumps(result, indent=2))
    print("\nDatabase transaction completed.")
    print("Old RustFS images and local uploads were NOT deleted.")
    print("Report:", RESULT_FILE)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as exc:
        print("\nMIGRATION FAILED:", str(exc))
        print("Database transaction will be rolled back if it had started.")
        raise
