from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base


class ModelProvider(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    api_key = Column(String(255), nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with ChatHistory
    chat_histories = relationship("ChatHistory", back_populates="model_provider")


class ChatHistory(Base):
    id = Column(Integer, primary_key=True, index=True)
    model_provider_id = Column(Integer, ForeignKey("modelprovider.id"))
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    chat_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with ModelProvider
    model_provider = relationship("ModelProvider", back_populates="chat_histories")
