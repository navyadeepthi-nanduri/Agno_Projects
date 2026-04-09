import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class Settings:
    APP_TITLE: str = os.getenv("APP_TITLE", "Gemma Multimodal Chatbot API")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1/chat/completions"
    )
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "google/gemma-3-27b-it:free"
    )

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_STT_MODEL: str = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")

    HTTP_REFERER: str = os.getenv("HTTP_REFERER", "http://localhost:7860")
    X_TITLE: str = os.getenv("X_TITLE", "Gemma Multimodal Chatbot")

    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    IMAGE_UPLOAD_DIR: Path = UPLOAD_DIR / "images"
    AUDIO_UPLOAD_DIR: Path = UPLOAD_DIR / "audio"


settings = Settings()

# Ensure upload folders exist
settings.IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)