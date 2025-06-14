from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional, List

from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.chat_models.base import BaseChatModel


class BaseModelService(ABC):
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self._model: Optional[BaseChatModel] = None

    @abstractmethod
    async def initialize_model(self) -> None:
        """Initialize the language model."""
        pass

    @abstractmethod
    async def generate_response(self, message: str, messages: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a response for the given message.
        
        Args:
            message: The current message to respond to
            messages: Optional list of previous messages in the conversation, each with 'role' and 'content'
        """
        pass

    @abstractmethod
    async def generate_stream(self, message: str, messages: Optional[List[Dict[str, str]]] = None) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response for the given message.
        
        Args:
            message: The current message to respond to
            messages: Optional list of previous messages in the conversation, each with 'role' and 'content'
        """
        pass

    def _convert_messages_to_langchain_format(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """Convert messages to LangChain format."""
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        return langchain_messages

    @property
    def model(self) -> BaseChatModel:
        if self._model is None:
            raise ValueError("Model not initialized. Call initialize_model() first.")
        return self._model

    @model.setter
    def model(self, value: BaseChatModel) -> None:
        self._model = value
