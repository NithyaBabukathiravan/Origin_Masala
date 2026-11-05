from pathlib import Path
import mimetypes
from app.core.rustfs_service import upload_image_to_rustfs

frontend_images = Path("../frontend/public/images")

for filename in ["co1.jpeg", "s2.jpeg", "t3.jpeg"]:
    file_path = frontend_images / filename

    content_type = mimetypes.guess_type(file_path.name)[0] or "image/jpeg"

    with open(file_path, "rb") as file:
        image_url = upload_image_to_rustfs(
            content=file.read(),
            content_type=content_type,
            original_filename=file_path.name,
        )

    print(f"{filename} -> {image_url}")
