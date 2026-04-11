import os
import requests

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SpeechToTextService:
    GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is missing in environment variables.")

        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_STT_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise RuntimeError(f"Audio file not found: {audio_path}")

        try:
            with open(audio_path, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(audio_path), audio_file, "application/octet-stream")
                }
                data = {
                    "model": self.model,
                    "response_format": "json",
                    "temperature": 0,
                }

                response = requests.post(
                    self.GROQ_STT_URL,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=settings.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

            transcription = result.get("text", "").strip()
            if not transcription:
                raise RuntimeError("Audio transcription returned empty text.")

            return transcription

        except requests.exceptions.Timeout:
            logger.exception("Groq STT request timed out.")
            raise RuntimeError("Groq speech-to-text request timed out.")
        except requests.exceptions.HTTPError as e:
            logger.exception("Groq STT HTTP error.")
            raise RuntimeError(f"Groq speech-to-text HTTP error: {str(e)} | {response.text}")
        except requests.exceptions.RequestException as e:
            logger.exception("Groq STT network error.")
            raise RuntimeError(f"Groq speech-to-text network error: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected transcription error.")
            raise RuntimeError(f"Speech transcription failed: {str(e)}")