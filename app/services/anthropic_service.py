from typing import AsyncGenerator, Dict, Any, Optional
import json

from langchain.chat_models import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from app.services.base import BaseModelService


class AnthropicService(BaseModelService):
    async def initialize_model(self) -> None:
        """Initialize the Anthropic chat model."""
        model_name = self.config.get("model_name", "claude-2.1")
        temperature = self.config.get("temperature", 0.7)
        streaming = self.config.get("streaming", False)
        max_tokens = self.config.get("max_tokens", 1024)
        
        self.model = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming,
            max_tokens_to_sample=max_tokens
        )

    async def generate_response(self, message: str) -> str:
        """Generate a response using the Anthropic chat model."""
        messages = [
            SystemMessage(content=self.config.get("system_message", "You are Claude, a helpful AI assistant.")),
            HumanMessage(content=message)
        ]
        
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text

    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the Anthropic chat model."""
        # Ensure streaming is enabled
        if not self.model.streaming:
            self.model = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model_name=self.config.get("model_name", "claude-2.1"),
                temperature=self.config.get("temperature", 0.7),
                streaming=True,
                max_tokens_to_sample=self.config.get("max_tokens", 1024)
            )

        messages = [
            SystemMessage(content=self.config.get("system_message", "You are Claude, a helpful AI assistant.")),
            HumanMessage(content=message)
        ]

        async for chunk in await self.model.astream([messages]):
            if chunk.content:
                yield chunk.content
