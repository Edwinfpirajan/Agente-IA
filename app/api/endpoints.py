from fastapi import APIRouter, Depends, HTTPException
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

def get_or_create_session(db: Session, user_id: str = "anon", service: str = "ALPHA"):
    session = (
        db.query(models.Session)
        .filter_by(user_id=user_id, service=service)
        .order_by(models.Session.started_at.desc())
        .first()
    )
    if not session:
        session = models.Session(user_id=user_id, service=service)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    try:
        question = payload.query
        user_id = payload.user_id
        service = "ALPHA"
        model_type = payload.model_type or "local"

        session_obj = get_or_create_session(db, user_id=user_id, service=service)

        history_records = (
            db.query(models.Conversation)
            .filter_by(session_id=session_obj.id)
            .order_by(models.Conversation.created_at.asc())
            .all()
        )
        history = [(conv.question, conv.answer) for conv in history_records]

        # Obtener respuesta con modelo seleccionado
        result = get_ai_response(question, history, user_id=user_id, model_type=model_type)

        # Guardar conversación
        convo = models.Conversation(
            question=question,
            answer=result["answer"],
            session_id=session_obj.id,
            service=service,
            model_ai=result["model_used"]
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)

        return {"question": question, "answer": result["answer"]}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
