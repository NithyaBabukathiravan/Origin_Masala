
import json
import mimetypes
from pathlib import Path

from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.rustfs_service import get_rustfs_client


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

PREVIEW_FILE = BASE_DIR / "image_migration_preview.json"
REPORT_FILE = BASE_DIR / "image_copy_report.json"

client = get_rustfs_client()


def content_type_for(filename):
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def source_bytes(old_url):
    filename = old_url.rsplit("/", 1)[-1]

    if old_url.startswith("/images/"):
        source_key = "images/" + filename

        response = client.get_object(
            Bucket=settings.rustfs_bucket_name,
            Key=source_key,
        )

        return response["Body"].read(), response.get(
            "ContentType",
            content_type_for(filename),
        )

    if old_url.startswith("/uploads/"):
        source_path = UPLOAD_DIR / filename

        if not source_path.is_file():
            raise FileNotFoundError(str(source_path))

        return source_path.read_bytes(), content_type_for(filename)

    raise ValueError(f"Unsupported source URL: {old_url}")


def verify_object(key):
    response = client.head_object(
        Bucket=settings.rustfs_bucket_name,
        Key=key,
    )

    return response.get("ContentLength", 0)


if not PREVIEW_FILE.is_file():
    raise SystemExit("ERROR: Migration preview file not found.")

preview = json.loads(PREVIEW_FILE.read_text(encoding="utf-8"))

if preview.get("missing_references") != 0:
    raise SystemExit("STOP: Missing source images exist. Copy cancelled.")

if not preview.get("mapping"):
    raise SystemExit("STOP: No image mappings found.")

mapping = preview["mapping"]

print("Unique images to copy:", len(mapping))
print("Database will NOT be updated.")
print("Old RustFS objects will NOT be deleted.")
print("Old local files will NOT be deleted.")

results = []
errors = []

for old_url, new_url in mapping.items():
    destination_key = new_url.lstrip("/").replace(
        "storage/image/", "", 1
    )

    try:
        # Never overwrite an existing destination object.
        try:
            client.head_object(
                Bucket=settings.rustfs_bucket_name,
                Key=destination_key,
            )
            raise RuntimeError(
                f"Destination already exists; refusing to overwrite: "
                f"{destination_key}"
            )
        except ClientError as exc:
            status = exc.response.get("ResponseMetadata", {}).get(
                "HTTPStatusCode"
            )
            error_code = exc.response.get("Error", {}).get("Code")

            if status != 404 and error_code not in (
                "404", "NoSuchKey", "NotFound"
            ):
                raise

        content, content_type = source_bytes(old_url)

        client.put_object(
            Bucket=settings.rustfs_bucket_name,
            Key=destination_key,
            Body=content,
            ContentType=content_type,
        )

        size = verify_object(destination_key)

        if size != len(content):
            raise RuntimeError(
                f"Size verification failed: expected {len(content)}, "
                f"found {size}"
            )

        results.append({
            "old_url": old_url,
            "new_url": new_url,
            "destination_key": destination_key,
            "content_type": content_type,
            "size_bytes": size,
            "verified": True,
        })

        print(f"OK: {old_url} -> {new_url}")

    except Exception as exc:
        errors.append({
            "old_url": old_url,
            "new_url": new_url,
            "error": str(exc),
        })

        print(f"FAILED: {old_url}: {exc}")


report = {
    "total_images": len(mapping),
    "copied_and_verified": len(results),
    "failed": len(errors),
    "database_updated": False,
    "old_objects_deleted": False,
    "results": results,
    "errors": errors,
}

REPORT_FILE.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("\n========== COPY REPORT ==========")
print("Total unique images:", len(mapping))
print("Copied and verified:", len(results))
print("Failed:", len(errors))
print("Database updated: NO")
print("Old objects deleted: NO")
print("Report:", REPORT_FILE)

if errors:
    print("\nSome images need attention. Do not update the database yet.")
else:
    print("\nAll images copied and verified successfully.")
