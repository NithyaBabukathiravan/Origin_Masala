import json
from sqlalchemy import text
from app.db.session import engine

checks = {
    "products": "image",
    "categories": "image_url",
    "recipes": "image",
    "recipe_categories": "image_url",
    "home_category_cards": "image_url",
}

total_old = 0

with engine.connect() as conn:
    print("========== IMAGE URL VERIFICATION ==========")

    for table, column in checks.items():
        rows = conn.execute(
            text(f"SELECT `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL")
        ).scalars().all()

        old = [
            value for value in rows
            if isinstance(value, str) and (
                value.startswith("/images/")
                or value.startswith("/uploads/")
                or "127.0.0.1:8000/uploads/" in value
            )
        ]

        new = [
            value for value in rows
            if isinstance(value, str)
            and value.startswith("/storage/image/site-images/")
        ]

        total_old += len(old)

        print(f"\n{table}.{column}")
        print("New RustFS URLs:", len(new))
        print("Old URLs remaining:", len(old))

        for value in old:
            print("OLD:", value)

    rows = conn.execute(
        text("SELECT config_json FROM homepage_config")
    ).scalars().all()

    homepage_old = []

    def scan(value, path="homepage_config"):
        if isinstance(value, dict):
            for key, item in value.items():
                scan(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                scan(item, f"{path}[{index}]")
        elif isinstance(value, str):
            if (
                value.startswith("/images/")
                or value.startswith("/uploads/")
                or "127.0.0.1:8000/uploads/" in value
            ):
                homepage_old.append((path, value))

    for raw in rows:
        config = json.loads(raw) if isinstance(raw, str) else raw
        scan(config)

    total_old += len(homepage_old)

    print("\nhomepage_config")
    print("Old URLs remaining:", len(homepage_old))

    for item in homepage_old:
        print("OLD:", item)

print("\n========== FINAL RESULT ==========")
print("Total old URL references remaining:", total_old)