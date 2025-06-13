from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ModelProvider Schemas
class ModelProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None


class ModelProviderCreate(ModelProviderBase):
    api_key: str = Field(..., min_length=1, max_length=255)


class ModelProviderUpdate(ModelProviderBase):
    api_key: Optional[str] = Field(None, min_length=1, max_length=255)


class ModelProviderInDB(ModelProviderBase):
    id: int
    api_key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ChatHistory Schemas
class ChatHistoryBase(BaseModel):
    user_message: str
    metadata: Optional[Dict[str, Any]] = None


class ChatHistoryCreate(ChatHistoryBase):
    model_provider_id: int


class ChatHistoryResponse(ChatHistoryBase):
    id: int
    assistant_message: str
    created_at: datetime
    model_provider: ModelProviderBase

    class Config:
        from_attributes = True


# Chat Request Schema
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model_provider_id: int = Field(..., gt=0)
    stream: bool = Field(default=False)
    metadata: Optional[Dict[str, Any]] = None
