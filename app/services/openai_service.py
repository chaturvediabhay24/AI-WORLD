from typing import AsyncGenerator, Dict, Any, Optional, List
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

    async def generate_response(self, message: str, messages: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response using the OpenAI chat model."""
        langchain_messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant."))
        ]
        
        # Add conversation history if provided
        if messages:
            langchain_messages.extend(self._convert_messages_to_langchain_format(messages))
        
        # Add current message
        langchain_messages.append(HumanMessage(content=message))
        
        response = await self.model.agenerate([langchain_messages])
        return response.generations[0][0].text

    async def generate_stream(self, message: str, messages: Optional[List[Dict[str, str]]] = None) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the OpenAI chat model."""
        # Ensure streaming is enabled
        if not self.model.streaming:
            self.model = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=self.config.get("model_name", "gpt-3.5-turbo"),
                temperature=self.config.get("temperature", 0.7),
                streaming=True
            )

        langchain_messages = [
            SystemMessage(content=self.config.get("system_message", "You are a helpful AI assistant."))
        ]
        
        # Add conversation history if provided
        if messages:
            langchain_messages.extend(self._convert_messages_to_langchain_format(messages))
        
        # Add current message
        langchain_messages.append(HumanMessage(content=message))

        async for chunk in self.model.astream(langchain_messages):
            if chunk.content:
                yield chunk.content
