from typing import List, Optional
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    user_input_used: str = Field(..., description="Combined user input sent to model")
    transcribed_audio: Optional[str] = Field(
        default=None,
        description="Transcribed audio text if audio was provided"
    )
    model_response: str = Field(..., description="Final assistant response")
    input_mode: str = Field(..., description="text / image / audio / multimodal")
    errors: List[str] = Field(default_factory=list, description="Any non-fatal errors")