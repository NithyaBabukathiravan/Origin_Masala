
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise SystemExit("DATABASE_URL missing in .env")

engine = create_engine(database_url, pool_pre_ping=True)
inspector = inspect(engine)

backup_dir = BASE_DIR / "database_backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backup_dir / f"origin_backup_{timestamp}.json"

backup = {
    "created_at": timestamp,
    "tables": {}
}

with engine.connect() as connection:
    table_names = inspector.get_table_names()

    for table_name in table_names:
        rows = connection.execute(
            text(f"SELECT * FROM `{table_name}`")
        ).mappings().all()

        backup["tables"][table_name] = [
            {
                key: (
                    value.isoformat()
                    if hasattr(value, "isoformat")
                    else value.hex()
                    if isinstance(value, bytes)
                    else value
                )
                for key, value in row.items()
            }
            for row in rows
        ]

backup_file.write_text(
    json.dumps(backup, indent=2, default=str),
    encoding="utf-8"
)

print("DATABASE BACKUP COMPLETED")
print("Tables:", len(backup["tables"]))
print("Backup:", backup_file)
for table, rows in backup["tables"].items():
    print(f"{table}: {len(rows)} rows")

engine.dispose()
