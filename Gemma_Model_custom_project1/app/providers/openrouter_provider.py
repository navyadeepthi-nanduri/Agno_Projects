import json
import mimetypes
import requests
from typing import Any, Dict, List

from app.config import settings
from app.providers.base_provider import BaseProvider
from app.services.image_utils import image_file_to_data_url
from app.prompts.system_prompts import GENERAL_ASSISTANT_SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterProvider(BaseProvider):
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is missing in environment variables.")

        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model_name = settings.MODEL_NAME
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.HTTP_REFERER,
            "X-Title": settings.X_TITLE,
        }

    def _post_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=settings.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.exception("OpenRouter request timed out.")
            raise RuntimeError("OpenRouter request timed out.")
        except requests.exceptions.HTTPError as e:
            error_text = ""
            try:
                error_text = response.text
            except Exception:
                pass
            logger.exception("OpenRouter HTTP error.")
            raise RuntimeError(f"OpenRouter HTTP error: {str(e)} | Response: {error_text}")
        except requests.exceptions.RequestException as e:
            logger.exception("OpenRouter network error.")
            raise RuntimeError(f"OpenRouter network error: {str(e)}")

    @staticmethod
    def _extract_response(data: Dict[str, Any]) -> str:
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"Invalid model response format: {json.dumps(data, indent=2)}")

    def _build_base_payload(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "messages": messages,
        }

    def chat_text(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": GENERAL_ASSISTANT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        payload = self._build_base_payload(messages)
        data = self._post_request(payload)
        return self._extract_response(data)

    def chat_with_image(self, prompt: str, image_path: str) -> str:
        image_data_url = image_file_to_data_url(image_path)

        messages = [
            {"role": "system", "content": GENERAL_ASSISTANT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ],
            },
        ]

        payload = self._build_base_payload(messages)

        try:
            data = self._post_request(payload)
            return self._extract_response(data)
        except RuntimeError as e:
            # Graceful handling if model may not support vision
            msg = str(e).lower()
            if "image" in msg or "vision" in msg or "content" in msg:
                raise RuntimeError(
                    "The selected OpenRouter model may not support image input. "
                    "Please switch to a vision-capable Gemma/OpenRouter model in .env."
                )
            raise