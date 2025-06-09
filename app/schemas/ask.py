from pydantic import BaseModel

class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    question: str
    answer: str
