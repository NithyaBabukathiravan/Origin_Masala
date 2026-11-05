
import json
import uuid
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import inspect, text

from app.db.session import engine
from app.core.config import settings
from app.core.rustfs_service import get_rustfs_client


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_FILE = BASE_DIR / "image_migration_preview.json"

TABLES = {
    "products": ["image"],
    "categories": ["image_url"],
    "recipes": ["image"],
    "recipe_categories": ["image_url"],
    "home_category_cards": ["image_url"],
}

client = get_rustfs_client()
inspector = inspect(engine)

# Same old URL will always receive the same planned new URL.
url_mapping = {}
records = []
errors = []


def normalize_url(value):
    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    if value.startswith("http://127.0.0.1:8000"):
        value = value.replace("http://127.0.0.1:8000", "", 1)
    elif value.startswith("http://localhost:8000"):
        value = value.replace("http://localhost:8000", "", 1)

    if value.startswith("/images/") or value.startswith("/uploads/"):
        return value

    return None


def check_source(old_url):
    filename = old_url.rsplit("/", 1)[-1]

    if old_url.startswith("/images/"):
        key = "images/" + filename

        try:
            client.head_object(
                Bucket=settings.rustfs_bucket_name,
                Key=key,
            )
            return True, "RustFS", key
        except Exception as exc:
            return False, "RustFS", str(exc)

    if old_url.startswith("/uploads/"):
        path = UPLOAD_DIR / filename

        if path.is_file():
            return True, "Local uploads", str(path)

        return False, "Local uploads", "File not found"

    return False, "Unknown", "Unsupported URL"


def plan_url(old_url):
    if old_url in url_mapping:
        return url_mapping[old_url]

    filename = old_url.rsplit("/", 1)[-1]
    extension = Path(filename).suffix.lower() or ".jpg"

    new_filename = f"{uuid.uuid4().hex}{extension}"
    new_url = f"/storage/image/site-images/{new_filename}"

    url_mapping[old_url] = new_url
    return new_url


def add_record(location, old_url):
    old_url = normalize_url(old_url)

    if not old_url:
        return

    exists, source_type, source_info = check_source(old_url)

    record = {
        "location": location,
        "old_url": old_url,
        "source_exists": exists,
        "source_type": source_type,
        "source_info": source_info,
        "new_url": plan_url(old_url) if exists else None,
    }

    records.append(record)

    if not exists:
        errors.append(record)


print("\nChecking database image references...\n")

with engine.connect() as conn:
    for table, image_columns in TABLES.items():

        if not inspector.has_table(table):
            print(f"SKIP: {table} table not found")
            continue

        columns = {
            column["name"]
            for column in inspector.get_columns(table)
        }

        primary_keys = inspector.get_pk_constraint(table).get(
            "constrained_columns", []
        )

        if not primary_keys:
            print(f"SKIP: {table} has no primary key")
            continue

        pk = primary_keys[0]

        selected_columns = [pk] + [
            col for col in image_columns if col in columns
        ]

        if len(selected_columns) == 1:
            continue

        sql = "SELECT " + ", ".join(
            f"`{col}`" for col in selected_columns
        ) + f" FROM `{table}`"

        rows = conn.execute(text(sql)).mappings().all()

        for row in rows:
            row_id = row[pk]

            for column in image_columns:
                if column not in columns:
                    continue

                old_url = row[column]

                add_record(
                    f"{table}.{row_id}.{column}",
                    old_url,
                )

    # homepage_config contains image URLs inside config_json.
    if inspector.has_table("homepage_config"):
        rows = conn.execute(
            text("SELECT id, config_json FROM homepage_config")
        ).mappings().all()

        def scan_json(obj, location):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current = f"{location}.{key}"

                    if key in ("image", "image_url"):
                        add_record(current, value)

                    scan_json(value, current)

            elif isinstance(obj, list):
                for index, value in enumerate(obj):
                    scan_json(value, f"{location}[{index}]")

        for row in rows:
            config = row["config_json"]

            if isinstance(config, str):
                config = json.loads(config)

            scan_json(config, f"homepage_config.{row['id']}")


report = {
    "database_updated": False,
    "rustfs_objects_copied": False,
    "total_references": len(records),
    "unique_images": len(url_mapping),
    "available_references": len(records) - len(errors),
    "missing_references": len(errors),
    "mapping": url_mapping,
    "records": records,
    "errors": errors,
}

OUTPUT_FILE.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("\n========== MIGRATION PREVIEW ==========")
print("Total references:", len(records))
print("Unique images:", len(url_mapping))
print("Available references:", len(records) - len(errors))
print("Missing references:", len(errors))
print("Database updated: NO")
print("RustFS objects copied: NO")
print("Report:", OUTPUT_FILE)

if errors:
    print("\nMISSING IMAGES:")
    for item in errors:
        print(item["location"], "->", item["old_url"])
else:
    print("\nAll referenced source images are available.")

print("\nPreview completed safely.")
