from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    question: str
    phone: str
    conversation_id: Optional[str] = None
    provider: Optional[str]
    model: Optional[str] = None 

class AskResponse(BaseModel):
    question: str
    answer: str
    
