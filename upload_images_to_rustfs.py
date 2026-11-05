
import os
import json
import mimetypes
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError
from dotenv import load_dotenv

# Load backend .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

FRONTEND_IMAGES = BASE_DIR.parent / "frontend" / "public" / "images"
OUTPUT_FILE = BASE_DIR / "rustfs_image_mapping.json"

ENDPOINT = os.getenv("RUSTFS_ENDPOINT_URL", "http://127.0.0.1:9000")
ACCESS_KEY = os.getenv("RUSTFS_ACCESS_KEY")
SECRET_KEY = os.getenv("RUSTFS_SECRET_KEY")
BUCKET = os.getenv("RUSTFS_BUCKET_NAME", "originmasala")
REGION = os.getenv("RUSTFS_REGION", "us-east-1")

if not ACCESS_KEY or not SECRET_KEY:
    raise SystemExit("ERROR: RustFS credentials missing in backend .env")

if not FRONTEND_IMAGES.exists():
    raise SystemExit(f"Images folder not found: {FRONTEND_IMAGES}")

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        connect_timeout=10,
        read_timeout=60,
        retries={"max_attempts": 3},
    ),
)

image_files = [
    path for path in FRONTEND_IMAGES.iterdir()
    if path.is_file() and path.suffix.lower() in {".jpeg", ".jpg", ".png", ".webp", ".gif"}
]

mapping = {}
success = 0
failed = []

print(f"\nFound {len(image_files)} image files.")
print(f"Target bucket: {BUCKET}\n")

# Check bucket access before uploading anything.
try:
    s3.head_bucket(Bucket=BUCKET)
except (ClientError, BotoCoreError) as exc:
    raise SystemExit(f"Cannot access RustFS bucket '{BUCKET}': {exc}")

for index, path in enumerate(image_files, start=1):
    object_key = f"images/{path.name}"
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

    try:
        with path.open("rb") as file:
            s3.put_object(
                Bucket=BUCKET,
                Key=object_key,
                Body=file,
                ContentType=content_type,
            )

        mapping[f"/images/{path.name}"] = f"/api/v1/images/{object_key}"
        success += 1
        print(f"[{index}/{len(image_files)}] OK  {path.name}")

    except (ClientError, BotoCoreError, OSError) as exc:
        failed.append({"file": path.name, "error": str(exc)})
        print(f"[{index}/{len(image_files)}] FAIL {path.name}: {exc}")

result = {
    "bucket": BUCKET,
    "uploaded_count": success,
    "failed_count": len(failed),
    "images": mapping,
    "failed": failed,
}

OUTPUT_FILE.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

print("\n========== UPLOAD SUMMARY ==========")
print(f"Uploaded: {success}")
print(f"Failed:   {len(failed)}")
print(f"Mapping:  {OUTPUT_FILE}")
print("====================================")
