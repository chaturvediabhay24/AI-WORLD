import pytest
from unittest.mock import AsyncMock, patch

from app.services.openai_service import OpenAIService
from app.services.factory import ModelServiceFactory


@pytest.fixture
def openai_service():
    return OpenAIService(
        api_key="test-key",
        config={
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "system_message": "You are a test assistant."
        }
    )


@pytest.mark.asyncio
async def test_openai_service_initialization(openai_service):
    await openai_service.initialize_model()
    assert openai_service.model is not None
    assert openai_service.model.model_name == "gpt-3.5-turbo"
    assert openai_service.model.temperature == 0.7


@pytest.mark.asyncio
async def test_openai_service_generate_response(openai_service):
    with patch('langchain.chat_models.ChatOpenAI.agenerate') as mock_generate:
        # Mock the response
        mock_response = AsyncMock()
        mock_response.generations = [[AsyncMock(text="Test response")]]
        mock_generate.return_value = mock_response

        await openai_service.initialize_model()
        response = await openai_service.generate_response("Test message")
        
        assert response == "Test response"
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_model_service_factory():
    service = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="openai",
        api_key="test-key",
        config={"model_name": "gpt-3.5-turbo"}
    )
    
    assert isinstance(service, OpenAIService)
    assert service.api_key == "test-key"
    
    # Test caching
    service2 = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="openai",
        api_key="test-key",
        config={"model_name": "gpt-3.5-turbo"}
    )
    
    assert service is service2  # Should return the same instance


@pytest.mark.asyncio
async def test_model_service_factory_unknown_provider():
    with pytest.raises(ValueError, match="Unknown model provider: unknown"):
        await ModelServiceFactory.get_service(
            provider_id=1,
            provider_name="unknown",
            api_key="test-key"
        )
