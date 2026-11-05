
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)
inspector = inspect(engine)

TARGET_TABLES = [
    "products",
    "categories",
    "recipes",
    "recipe_categories",
    "home_category_cards",
    "homepage_config",
]

def clean_value(value):
    if isinstance(value, bytes):
        return value.hex()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value

report = {}

with engine.connect() as connection:
    for table in TARGET_TABLES:
        if table not in inspector.get_table_names():
            continue

        columns = inspector.get_columns(table)
        image_columns = [
            col["name"]
            for col in columns
            if any(word in col["name"].lower()
                   for word in ["image", "photo", "picture", "banner"])
        ]

        print(f"\n===== {table} =====")
        print("Image-related columns:", image_columns or "None")

        table_report = []

        if image_columns:
            rows = connection.execute(
                text(f"SELECT * FROM `{table}`")
            ).mappings().all()

            for row in rows:
                item = {}
                for column in image_columns:
                    value = row[column]
                    if value not in (None, ""):
                        item[column] = clean_value(value)

                if item:
                    # Include row ID when available
                    for key in ("id", "uuid", "name", "title"):
                        if key in row:
                            item["_row_" + key] = clean_value(row[key])
                    table_report.append(item)

                    print(json.dumps(item, ensure_ascii=False, default=str))

        report[table] = {
            "image_columns": image_columns,
            "rows": table_report,
        }

output = BASE_DIR / "image_url_audit.json"
output.write_text(
    json.dumps(report, indent=2, ensure_ascii=False, default=str),
    encoding="utf-8",
)

print("\nAudit completed. No database values were changed.")
print("Report:", output)

engine.dispose()
