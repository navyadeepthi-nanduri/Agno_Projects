from pathlib import Path


class FileValidationError(ValueError):
    pass


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm"}


def validate_image_file(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported image file type: {ext}. "
            f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )


def validate_audio_file(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported audio file type: {ext}. "
            f"Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )