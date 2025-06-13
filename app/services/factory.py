from typing import Dict, Optional, Type
from app.services.base import BaseModelService
from app.services.openai_service import OpenAIService
from app.services.perplexity_service import PerplexityService
from app.services.anthropic_service import AnthropicService


class ModelServiceFactory:
    _services: Dict[str, Type[BaseModelService]] = {
        "openai": OpenAIService,
        "perplexity": PerplexityService,
        "anthropic": AnthropicService,
    }
    
    _instances: Dict[int, BaseModelService] = {}

    @classmethod
    def register_service(cls, name: str, service_class: Type[BaseModelService]) -> None:
        """Register a new model service."""
        cls._services[name.lower()] = service_class

    @classmethod
    async def get_service(cls, provider_id: int, provider_name: str, api_key: str, config: Optional[Dict] = None) -> BaseModelService:
        """Get or create a model service instance."""
        if provider_id not in cls._instances:
            service_class = cls._services.get(provider_name.lower())
            if not service_class:
                raise ValueError(f"Unknown model provider: {provider_name}")
            
            service = service_class(api_key=api_key, config=config)
            await service.initialize_model()
            cls._instances[provider_id] = service
        
        return cls._instances[provider_id]

    @classmethod
    def remove_service(cls, provider_id: int) -> None:
        """Remove a model service instance."""
        if provider_id in cls._instances:
            del cls._instances[provider_id]
