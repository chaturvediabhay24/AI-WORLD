from typing import AsyncGenerator, Dict, Any, Optional
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from app.services.base import BaseModelService


class OpenAIService(BaseModelService):
    async def initialize_model(self) -> None:
        """Initialize the OpenAI chat model."""
        model_name = self.config.get("model_name", "gpt-3.5-turbo")
        temperature = self.config.get("temperature", 0.7)
        streaming = self.config.get("streaming", False)
        
        self.model = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming
        )

    async def generate_response(self, message: str) -> str:
        """Generate a response using the OpenAI chat model."""
        messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant.")),
            HumanMessage(content=message)
        ]
        
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text

    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the OpenAI chat model."""
        # Ensure streaming is enabled
        if not self.model.streaming:
            self.model = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=self.config.get("model_name", "gpt-3.5-turbo"),
                temperature=self.config.get("temperature", 0.7),
                streaming=True
            )

        messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant.")),
            HumanMessage(content=message)
        ]

        async for chunk in self.model.astream(messages):
            if chunk.content:
                yield chunk.content
