from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.orchestrator import ChatOrchestrator
from app.schemas import ChatResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    text_input: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    audio: Optional[UploadFile] = File(default=None),
):
    try:
        orchestrator = ChatOrchestrator()
        result = await orchestrator.handle_request(
            text_input=text_input,
            image_file=image,
            audio_file=audio,
        )
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected server error")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")