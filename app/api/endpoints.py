from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from typing import Optional, Union
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
# from app.schemas.ask import AskRequest, AskResponse
from app.db.database import SessionLocal
from app.db import models
from app.integrations.document_handler import DocumentHandler
from app.services.chatbot import get_answer_for_agent
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.tools.voice import transcribe_and_cleanup 
from app.tools.image import analyze_image, encode_image
from dotenv import load_dotenv
from openai import OpenAI
from requests.auth import HTTPBasicAuth
import requests
import os
import base64
from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

load_dotenv()
router = APIRouter()
document_handler = DocumentHandler()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def get_or_create_session(db: Session, phone: str = "anon", service: str = "ALPHA"):
    session = (
        db.query(models.Session)
        .filter_by(phone=phone, service=service)
        .order_by(models.Session.started_at.desc())
        .first()
    )
    if not session:
        session = models.Session(phone=phone, service=service)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

@router.post("/ask")
async def ask_question(
    text: Union[str, None] = Form(default=None),
    image: Union[UploadFile, None] = File(default=None),
    audio: Union[UploadFile, None] = File(default=None),
    db: Session = Depends(get_db)
):
    try:
        service = "Alpha"
        user_phone = "123"
        model = "gpt-4.1-2025-04-14"


        input_text = ""
        if text and text.strip():
            input_text = text.strip()


        elif image:
            try:
                image_content = await image.read()
                input_text = analyze_image(image_content)
            except Exception as e:
                print(f"Error procesando imagen: {e}")

        elif audio:
            try:
                audio_data = await audio.read()
                input_text = transcribe_and_cleanup(audio_data)
            except Exception as e:
                print(f"Error procesando audio: {e}")
                if not input_text:
                    raise HTTPException(400, "Error con el audio y no hay texto de respaldo")
                
        else:
            raise HTTPException(400, "No se recibió texto, imagen o audio para procesar")
      
    except Exception as e:
        print(f"Error en la solicitud: {str(e)}")
        raise HTTPException(500, "Error procesando la solicitud")
    
        
    if not input_text or input_text.strip() == "":
        raise HTTPException(400, "No se recibió contenido válido para procesar")

    try:
        session_obj = get_or_create_session(db, phone=user_phone, service=service)

        # Obtener historial
        history_records = (
            db.query(models.Conversation)
            .filter_by(session_id=session_obj.id)
            .order_by(models.Conversation.created_at.asc())
            .all()
        )
        history = [(conv.question, conv.answer) for conv in history_records]

        result = get_answer_for_agent(
            question=input_text,
            history=history,
            model_used=model,
            phone=user_phone
        )

        # Guardar en DB
        convo = models.Conversation(
            question=input_text,
            answer=result["answer"],
            session_id=session_obj.id,
            service=service,
            model_ai=result["model_used"]
        )
        db.add(convo)
        db.commit()

        return result["answer"]

    except Exception as e:
        db.rollback()
        print(f"Error en procesamiento principal: {str(e)}")
        raise HTTPException(500, "Error generando respuesta")



@router.post("/documents-upload")
async def upload_docoment(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_name = file.filename

    try:
        metadata = {
            "source": file_name,
            "file_type": file.content_type
        }
        result = document_handler.ingest_file_bytes(file_bytes, file_name, metadata)
        
        return JSONResponse(content={"message": "Documento procesado correctamente.", "result": result}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "Error al procesar el documento.", "error": str(e)}, status_code=500)

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "El servidor y la api funcionan correctamente."}





