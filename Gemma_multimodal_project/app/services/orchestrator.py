from typing import Optional, List
from fastapi import UploadFile

from app.providers.provider_factory import ProviderFactory
from app.schemas import ChatResponse
from app.services.speech_to_text_service import SpeechToTextService
from app.services.file_validation import (
    validate_image_file,
    validate_audio_file,
    FileValidationError,
)
from app.prompts.system_prompts import DEFAULT_IMAGE_ONLY_PROMPT
from app.config import settings
from app.utils.helpers import save_upload_file
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatOrchestrator:
    def __init__(self):
        self.provider = ProviderFactory.get_provider("openrouter")

    @staticmethod
    def _determine_input_mode(
        has_text: bool,
        has_image: bool,
        has_audio: bool
    ) -> str:
        count = sum([has_text, has_image, has_audio])

        if count == 0:
            return "none"
        if count > 1:
            return "multimodal"
        if has_text:
            return "text"
        if has_image:
            return "image"
        if has_audio:
            return "audio"
        return "unknown"

    async def handle_request(
        self,
        text_input: Optional[str] = None,
        image_file: Optional[UploadFile] = None,
        audio_file: Optional[UploadFile] = None,
    ) -> ChatResponse:
        errors: List[str] = []

        text_input = (text_input or "").strip()
        has_text = bool(text_input)
        has_image = image_file is not None
        has_audio = audio_file is not None

        input_mode = self._determine_input_mode(has_text, has_image, has_audio)

        if input_mode == "none":
            raise ValueError("No input provided. Please provide text, image, audio, or a combination.")

        image_path = None
        audio_path = None
        transcribed_audio = None

        # Save + validate image
        if has_image:
            try:
                validate_image_file(image_file.filename)
                image_path = save_upload_file(image_file, settings.IMAGE_UPLOAD_DIR)
            except FileValidationError as e:
                raise ValueError(str(e))
            except Exception as e:
                raise RuntimeError(f"Failed to save image file: {str(e)}")

        # Save + validate audio
        if has_audio:
            try:
                validate_audio_file(audio_file.filename)
                audio_path = save_upload_file(audio_file, settings.AUDIO_UPLOAD_DIR)
            except FileValidationError as e:
                raise ValueError(str(e))
            except Exception as e:
                raise RuntimeError(f"Failed to save audio file: {str(e)}")

        # Transcribe audio if present
        if audio_path:
            try:
                stt_service = SpeechToTextService()
                transcribed_audio = stt_service.transcribe(audio_path)
            except Exception as e:
                errors.append(str(e))
                # If only audio and transcription failed, we can't continue meaningfully
                if not has_text and not has_image:
                    raise RuntimeError(
                        "Audio was provided but transcription failed, and no other usable input exists."
                    )

        # Build final prompt
        final_prompt_parts = []

        if has_text:
            final_prompt_parts.append(f"User typed input:\n{text_input}")

        if transcribed_audio:
            final_prompt_parts.append(f"Transcribed audio input:\n{transcribed_audio}")

        # If image only and no text/transcribed audio, use default prompt
        if has_image and not final_prompt_parts:
            final_prompt = DEFAULT_IMAGE_ONLY_PROMPT
        else:
            if has_image:
                final_prompt_parts.append(
                    "There is also an uploaded image. Analyze the image carefully and use it along with the text/audio context."
                )

            final_prompt = "\n\n".join(final_prompt_parts).strip()

        if not final_prompt and not has_image:
            raise ValueError("No usable input after processing. Please provide valid text, image, or audio.")

        # Call provider
        try:
            if has_image:
                model_response = self.provider.chat_with_image(
                    prompt=final_prompt,
                    image_path=image_path,
                )
            else:
                model_response = self.provider.chat_text(prompt=final_prompt)
        except Exception as e:
            raise RuntimeError(str(e))

        user_input_used = final_prompt

        return ChatResponse(
            user_input_used=user_input_used,
            transcribed_audio=transcribed_audio,
            model_response=model_response,
            input_mode=input_mode,
            errors=errors,
        )