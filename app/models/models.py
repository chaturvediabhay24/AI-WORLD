from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship

from sqlalchemy.orm import DeclarativeBase, Mapped
from app.database.base import Base

# Association table for provider-tool relationship
provider_tools = Table(
    'provider_tools',
    Base.metadata,
    Column('provider_id', Integer, ForeignKey('modelprovider.id', ondelete='CASCADE')),
    Column('tool_id', String(50)),
)


class ModelProvider(Base):
    __tablename__ = "modelprovider"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(50), index=True, nullable=False)  # Removed unique=True
    api_key: Mapped[str] = Column(String(255), nullable=False)
    config: Mapped[Optional[Dict]] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat_histories = relationship("ChatHistory", back_populates="model_provider")
    tool_ids = Column(JSON, nullable=True, default=list)  # List of tool IDs enabled for this provider


class ChatHistory(Base):
    __tablename__ = "chathistory"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = Column(String(50), index=True, nullable=True)
    model_provider_id: Mapped[int] = Column(Integer, ForeignKey("modelprovider.id"))
    user_message: Mapped[str] = Column(Text, nullable=False)
    assistant_message: Mapped[str] = Column(Text, nullable=False)
    chat_metadata: Mapped[Optional[Dict]] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    # Relationship with ModelProvider
    model_provider = relationship("ModelProvider", back_populates="chat_histories")
