from pathlib import Path
from app.core.rustfs_service import upload_image_to_rustfs

file_path = Path("../frontend/public/images/w1.jpeg")

if not file_path.exists():
    print("ERROR: w1.jpeg not found")
else:
    with open(file_path, "rb") as file:
        url = upload_image_to_rustfs(
            content=file.read(),
            content_type="image/jpeg",
            original_filename="w1.jpeg",
        )
    print(f"w1.jpeg -> {url}")
