from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """Schema for tool parameter definition."""
    name: str
    type: str  # e.g., "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """Schema for tool definition."""
    id: str
    name: str
    description: str
    parameters: list[ToolParameter]
    provider_id: int


class BaseTool(ABC):
    """Base class for all tools."""
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Get the tool definition."""
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass

    @classmethod
    def create(cls, provider_id: int, **kwargs) -> 'BaseTool':
        """Create a new instance of the tool."""
        return cls(provider_id=provider_id, **kwargs)
