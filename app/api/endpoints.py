from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ask import AskRequest, AskResponse
from app.db.database import SessionLocal
from app.db import models
from app.services.chatbot import get_ai_response

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    question = payload.query
    answer = get_ai_response(question)

    convo = models.Conversation(question=question, answer=answer)
    db.add(convo)
    db.commit()
    db.refresh(convo)

    return {"question": question, "answer": answer}
