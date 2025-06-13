from typing import AsyncGenerator, Dict, Any, Optional
import json

from langchain.chat_models import ChatPerplexity
from langchain.schema import HumanMessage, SystemMessage

from app.services.base import BaseModelService


class PerplexityService(BaseModelService):
    async def initialize_model(self) -> None:
        """Initialize the Perplexity chat model."""
        model_name = self.config.get("model_name", "pplx-7b-chat")
        temperature = self.config.get("temperature", 0.7)
        streaming = self.config.get("streaming", False)
        
        self.model = ChatPerplexity(
            api_key=self.api_key,
            model=model_name,
            temperature=temperature,
            streaming=streaming
        )

    async def generate_response(self, message: str) -> str:
        """Generate a response using the Perplexity chat model."""
        messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant.")),
            HumanMessage(content=message)
        ]
        
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text

    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the Perplexity chat model."""
        # Ensure streaming is enabled
        if not self.model.streaming:
            self.model = ChatPerplexity(
                api_key=self.api_key,
                model=self.config.get("model_name", "pplx-7b-chat"),
                temperature=self.config.get("temperature", 0.7),
                streaming=True
            )

        messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant.")),
            HumanMessage(content=message)
        ]

        async for chunk in await self.model.astream([messages]):
            if chunk.content:
                yield chunk.content
