from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from sqlalchemy.orm import DeclarativeBase, Mapped
from app.database.base import Base


class ModelProvider(Base):
    __tablename__ = "modelprovider"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    api_key: Mapped[str] = Column(String(255), nullable=False)
    config: Mapped[Optional[Dict]] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with ChatHistory
    chat_histories = relationship("ChatHistory", back_populates="model_provider")


class ChatHistory(Base):
    __tablename__ = "chathistory"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    model_provider_id: Mapped[int] = Column(Integer, ForeignKey("modelprovider.id"))
    user_message: Mapped[str] = Column(Text, nullable=False)
    assistant_message: Mapped[str] = Column(Text, nullable=False)
    chat_metadata: Mapped[Optional[Dict]] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    # Relationship with ModelProvider
    model_provider = relationship("ModelProvider", back_populates="chat_histories")
