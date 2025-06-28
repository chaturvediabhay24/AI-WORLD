from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.tools.base import ToolParameter, ToolDefinition

# Tool Schemas
class ToolExecuteRequest(BaseModel):
    """Schema for tool execution request."""
    tool_id: str = Field(..., description="ID of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the tool execution")


class ToolExecuteResponse(BaseModel):
    """Schema for tool execution response."""
    result: Any = Field(..., description="Result of the tool execution")
    tool_id: str = Field(..., description="ID of the executed tool")


class ToolListResponse(BaseModel):
    """Schema for listing available tools."""
    tools: List[ToolDefinition] = Field(..., description="List of available tools")


# ModelProvider Schemas
class ModelProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None
    tool_ids: Optional[List[str]] = Field(default_factory=list, description="List of enabled tool IDs")

    class Config:
        from_attributes = True
        populate_by_name = True


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
        populate_by_name = True


# ChatHistory Schemas
class ChatHistoryBase(BaseModel):
    user_message: str
    chat_metadata: Optional[Dict[str, Any]] = None
    tool_request: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None


class ChatHistoryCreate(ChatHistoryBase):
    model_provider_id: int


class ChatHistoryResponse(ChatHistoryBase):
    id: int
    conversation_id: Optional[str]
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
    conversation_id: Optional[str] = Field(None, min_length=1, max_length=50)
    chat_metadata: Optional[Dict[str, Any]] = None
