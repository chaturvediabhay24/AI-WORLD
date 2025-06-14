from typing import Dict, List, Type
from app.tools.base import BaseTool, ToolDefinition


class ToolRegistry:
    """Registry for managing available tools."""
    
    _tools: Dict[str, Type[BaseTool]] = {}
    _instances: Dict[int, Dict[str, BaseTool]] = {}  # provider_id -> {tool_id -> tool_instance}

    @classmethod
    def register_tool(cls, tool_class: Type[BaseTool]) -> None:
        """Register a new tool class."""
        # Create temporary instance to get tool ID
        temp_instance = tool_class.create(provider_id=0)
        tool_id = temp_instance.get_definition().id
        cls._tools[tool_id] = tool_class

    @classmethod
    def get_tool_class(cls, tool_id: str) -> Type[BaseTool]:
        """Get a tool class by its ID."""
        if tool_id not in cls._tools:
            raise ValueError(f"Tool {tool_id} not found")
        return cls._tools[tool_id]

    @classmethod
    def get_available_tools(cls) -> List[Type[BaseTool]]:
        """Get all registered tool classes."""
        return list(cls._tools.values())

    @classmethod
    def create_tool_instance(cls, tool_id: str, provider_id: int) -> BaseTool:
        """Create a new instance of a tool for a provider."""
        tool_class = cls.get_tool_class(tool_id)
        
        # Initialize provider's tool dictionary if it doesn't exist
        if provider_id not in cls._instances:
            cls._instances[provider_id] = {}
        
        # Create and store tool instance
        instance = tool_class.create(provider_id=provider_id)
        cls._instances[provider_id][tool_id] = instance
        return instance

    @classmethod
    def get_tool_instance(cls, tool_id: str, provider_id: int) -> BaseTool:
        """Get a tool instance for a provider."""
        if provider_id not in cls._instances or tool_id not in cls._instances[provider_id]:
            return cls.create_tool_instance(tool_id, provider_id)
        return cls._instances[provider_id][tool_id]

    @classmethod
    def get_provider_tools(cls, provider_id: int) -> List[ToolDefinition]:
        """Get all tool definitions for a provider."""
        if provider_id not in cls._instances:
            return []
        return [
            tool.get_definition()
            for tool in cls._instances[provider_id].values()
        ]

    @classmethod
    def remove_provider_tools(cls, provider_id: int) -> None:
        """Remove all tools for a provider."""
        if provider_id in cls._instances:
            del cls._instances[provider_id]
