from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional

from langchain.schema import BaseMessage
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
    async def generate_response(self, message: str) -> str:
        """Generate a response for the given message."""
        pass

    @abstractmethod
    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response for the given message."""
        pass

    @property
    def model(self) -> BaseChatModel:
        if self._model is None:
            raise ValueError("Model not initialized. Call initialize_model() first.")
        return self._model

    @model.setter
    def model(self, value: BaseChatModel) -> None:
        self._model = value
