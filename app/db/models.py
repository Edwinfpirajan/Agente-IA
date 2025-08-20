from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(100), nullable=True)  # si identificas al usuario
    conversation_id = Column(String(100), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    service = Column(String(50), nullable=False, default="ALPHA")

    conversations = relationship("Conversation", back_populates="session")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    service = Column(String(50), nullable=False, default="ALPHA")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="conversations")
    model_ai = Column(String(50), nullable=True)
