from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from app.database.base import get_db
from app.models.models import ModelProvider, ChatHistory
from app.schemas.schemas import ChatRequest, ChatHistoryResponse, ModelProviderBase
from app.services.factory import ModelServiceFactory
from app.core.config import settings

router = APIRouter()


async def get_provider_or_404(provider_id: int, db: AsyncSession) -> ModelProvider:
    """Get provider or raise 404 error."""
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/chat", response_model=ChatHistoryResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a chat response using the specified model provider."""
    provider = await get_provider_or_404(request.model_provider_id, db)

    # Get API key from environment/config, not from DB
    api_key = None
    if provider.name.lower() == "openai":
        api_key = settings.OPENAI_API_KEY
    elif provider.name.lower() == "anthropic":
        api_key = settings.ANTHROPIC_API_KEY
    elif provider.name.lower() == "perplexity":
        api_key = settings.PERPLEXITY_API_KEY
    else:
        raise HTTPException(status_code=400, detail="Unknown provider for API key")
    if not api_key:
        raise HTTPException(status_code=500, detail=f"API key for {provider.name} not set in environment")

    try:
        # Get model service
        service = await ModelServiceFactory.get_service(
            provider_id=provider.id,
            provider_name=provider.name,
            api_key=api_key,
            config=provider.config
        )
        
        # Generate response
        response = await service.generate_response(request.message)
        
        # Save chat history
        chat_history = ChatHistory(
            model_provider_id=provider.id,
            user_message=request.message,
            assistant_message=response,
            chat_metadata=request.chat_metadata
        )
        db.add(chat_history)
        await db.commit()
        await db.refresh(chat_history)

        # Eagerly load model_provider relationship
        from sqlalchemy import select
        stmt = (
            select(ChatHistory)
            .options(selectinload(ChatHistory.model_provider))
            .where(ChatHistory.id == chat_history.id)
        )
        result = await db.execute(stmt)
        chat_history_with_provider = result.scalar_one()

        # Manually construct the response to ensure model_provider is a Pydantic model
        return ChatHistoryResponse(
            id=chat_history_with_provider.id,
            user_message=chat_history_with_provider.user_message,
            assistant_message=chat_history_with_provider.assistant_message,
            chat_metadata=chat_history_with_provider.chat_metadata,
            created_at=chat_history_with_provider.created_at,
            model_provider=ModelProviderBase.from_orm(chat_history_with_provider.model_provider)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a streaming chat response using the specified model provider."""
    if not request.stream:
        raise HTTPException(status_code=400, detail="Streaming must be enabled for this endpoint")
    
    provider = await get_provider_or_404(request.model_provider_id, db)

    # Get API key from environment/config, not from DB
    api_key = None
    if provider.name.lower() == "openai":
        api_key = settings.OPENAI_API_KEY
    elif provider.name.lower() == "anthropic":
        api_key = settings.ANTHROPIC_API_KEY
    elif provider.name.lower() == "perplexity":
        api_key = settings.PERPLEXITY_API_KEY
    else:
        raise HTTPException(status_code=400, detail="Unknown provider for API key")
    if not api_key:
        raise HTTPException(status_code=500, detail=f"API key for {provider.name} not set in environment")
    
    try:
        # Get model service
        service = await ModelServiceFactory.get_service(
            provider_id=provider.id,
            provider_name=provider.name,
            api_key=api_key,
            config=provider.config
        )
        
        # Create generator function for streaming
        async def event_generator():
            full_response = []
            async for chunk in service.generate_stream(request.message):
                full_response.append(chunk)
                yield {
                    "event": "message",
                    "data": chunk
                }
            
            # Save chat history after completion
            chat_history = ChatHistory(
                model_provider_id=provider.id,
                user_message=request.message,
                assistant_message="".join(full_response),
                chat_metadata=request.chat_metadata
            )
            db.add(chat_history)
            await db.commit()
        
        return EventSourceResponse(event_generator())
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{provider_id}", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a specific provider."""
    await get_provider_or_404(provider_id, db)
    
    from sqlalchemy import select
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.model_provider_id == provider_id)
        .order_by(ChatHistory.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
