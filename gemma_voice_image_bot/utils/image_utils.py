import base64
import os

def load_image_base64(image_path: str):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    # Detect mime type from extension
    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".png":
        mime_type = "image/png"
    else:
        mime_type = "image/jpeg"

    return image_b64, mime_type