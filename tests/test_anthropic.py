import pytest
from unittest.mock import AsyncMock, patch

from app.services.anthropic_service import AnthropicService
from app.services.factory import ModelServiceFactory


@pytest.fixture
def anthropic_service():
    return AnthropicService(
        api_key="test-key",
        config={
            "model_name": "claude-2.1",
            "temperature": 0.7,
            "system_message": "You are a test assistant.",
            "max_tokens": 1024
        }
    )


@pytest.mark.asyncio
async def test_anthropic_service_initialization(anthropic_service):
    await anthropic_service.initialize_model()
    assert anthropic_service.model is not None
    assert anthropic_service.model.model_name == "claude-2.1"
    assert anthropic_service.model.temperature == 0.7
    assert anthropic_service.model.max_tokens_to_sample == 1024


@pytest.mark.asyncio
async def test_anthropic_service_generate_response(anthropic_service):
    with patch('langchain.chat_models.ChatAnthropic.agenerate') as mock_generate:
        # Mock the response
        mock_response = AsyncMock()
        mock_response.generations = [[AsyncMock(text="Test response")]]
        mock_generate.return_value = mock_response

        await anthropic_service.initialize_model()
        response = await anthropic_service.generate_response("Test message")
        
        assert response == "Test response"
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_anthropic_service_streaming(anthropic_service):
    with patch('langchain.chat_models.ChatAnthropic.astream') as mock_stream:
        # Mock the streaming response
        async def mock_astream(*args, **kwargs):
            chunks = [
                AsyncMock(content="Hello"),
                AsyncMock(content=" from"),
                AsyncMock(content=" Claude!")
            ]
            for chunk in chunks:
                yield chunk

        mock_stream.return_value = mock_astream()

        await anthropic_service.initialize_model()
        chunks = []
        async for chunk in await anthropic_service.generate_stream("Test message"):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " from", " Claude!"]
        mock_stream.assert_called_once()


@pytest.mark.asyncio
async def test_model_service_factory_anthropic():
    service = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="anthropic",
        api_key="test-key",
        config={
            "model_name": "claude-2.1",
            "max_tokens": 1024
        }
    )
    
    assert isinstance(service, AnthropicService)
    assert service.api_key == "test-key"
    
    # Test caching
    service2 = await ModelServiceFactory.get_service(
        provider_id=1,
        provider_name="anthropic",
        api_key="test-key",
        config={
            "model_name": "claude-2.1",
            "max_tokens": 1024
        }
    )
    
    assert service is service2  # Should return the same instance


@pytest.mark.asyncio
async def test_anthropic_service_with_different_models():
    # Test with claude-3-opus
    service_opus = AnthropicService(
        api_key="test-key",
        config={
            "model_name": "claude-3-opus",
            "temperature": 0.5
        }
    )
    await service_opus.initialize_model()
    assert service_opus.model.model_name == "claude-3-opus"

    # Test with claude-3-sonnet
    service_sonnet = AnthropicService(
        api_key="test-key",
        config={
            "model_name": "claude-3-sonnet",
            "temperature": 0.5
        }
    )
    await service_sonnet.initialize_model()
    assert service_sonnet.model.model_name == "claude-3-sonnet"
