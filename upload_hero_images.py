from pathlib import Path
import mimetypes

from app.core.rustfs_service import upload_image_to_rustfs

FRONTEND_IMAGES = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "public"
    / "images"
)

HERO_FILES = ["h12.jpeg", "h13.jpeg", "h3.jpeg"]

for filename in HERO_FILES:
    image_path = FRONTEND_IMAGES / filename

    if not image_path.exists():
        print(f"NOT FOUND: {image_path}")
        continue

    content_type, _ = mimetypes.guess_type(str(image_path))

    if not content_type:
        print(f"UNKNOWN IMAGE TYPE: {filename}")
        continue

    try:
        image_url = upload_image_to_rustfs(
            content=image_path.read_bytes(),
            content_type=content_type,
            original_filename=filename,
        )
        print(f"{filename} -> {image_url}")

    except Exception as exc:
        print(f"FAILED: {filename}: {exc}")