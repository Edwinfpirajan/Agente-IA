from pydantic import BaseModel

class AskRequest(BaseModel):
    user_id: str
    query: str
class AskResponse(BaseModel):
    question: str
    answer: str
    
