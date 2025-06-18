from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    query: str
    user_id: str
    provider: Optional[str]
    model: Optional[str] = None 
class AskResponse(BaseModel):
    question: str
    answer: str
    
