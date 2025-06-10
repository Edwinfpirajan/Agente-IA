from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    query: str
    user_id: str
    model_type: Optional[str]
class AskResponse(BaseModel):
    question: str
    answer: str
    
