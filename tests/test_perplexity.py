import pytest
from unittest.mock import AsyncMock, patch

from app.services.perplexity_service import PerplexityService
from app.services.factory import ModelServiceFactory


@pytest.fixture
def perplexity_service():
    return PerplexityService(
        api_key="test-key",
        config={
            "model_name": "pplx-7b-chat",
            "temperature": 0.7,
            "system_message": "You are a test assistant."
        }
    )


@pytest.mark.asyncio
async def test_perplexity_service_initialization(perplexity_service):
    await perplexity_service.initialize_model()
    assert perplexity_service.model is not None
    assert perplexity_service.model.model == "pplx-7b-chat"
    assert perplexity_service.model.temperature == 0.7


@pytest.mark.asyncio
async def test_perplexity_service_generate_response(perplexity_service):
    with patch('langchain.chat_models.ChatPerplexity.agenerate') as mock_generate:
        # Mock the response
        mock_response = AsyncMock()
        mock_response.generations = [[AsyncMock(text="Test response")]]
        mock_generate.return_value = mock_response

        await perplexity_service.initialize_model()
        response = await perplexity_service.generate_response("Test message")
        
        assert response == "Test response"
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_perplexity_service_streaming(perplexity_service):
    with patch('langchain.chat_models.ChatPerplexity.astream') as mock_stream:
        # Mock the streaming response
        async def mock_astream(*args, **kwargs):
            chunks = [
                AsyncMock(content="Hello"),
                AsyncMock(content=" World"),
                AsyncMock(content="!")
            ]
            for chunk in chunks:
                yield chunk

        mock_stream.return_value = mock_astream()

        await perplexity_service.initialize_model()
        chunks = []
        async for chunk in await perplexity_service.generate_stream("Test message"):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " World", "!"]
        mock_stream.assert_called_once()


@pytest.mark.asyncio
async def test_model_service_factory_perplexity():
    service = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="perplexity",
        api_key="test-key",
        config={"model_name": "pplx-7b-chat"}
    )
    
    assert isinstance(service, PerplexityService)
    assert service.api_key == "test-key"
    
    # Test caching
    service2 = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="perplexity",
        api_key="test-key",
        config={"model_name": "pplx-7b-chat"}
    )
    
    assert service is service2  # Should return the same instance
