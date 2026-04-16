import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile


def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> str:
    destination_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(upload_file.filename).name
    suffix = Path(original_name).suffix
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    destination_path = destination_dir / unique_name

    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(destination_path)