import base64
import mimetypes
from pathlib import Path


def image_file_to_data_url(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = "image/png"

    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"