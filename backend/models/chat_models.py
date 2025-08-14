from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    patient_id: Optional[int] = None

class BotResponse(BaseModel):
    response: str
    conversation_id: str
