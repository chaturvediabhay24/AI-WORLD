from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database.base import get_db
from app.models.models import ModelProvider, ChatHistory
from app.schemas.schemas import ChatRequest, ChatHistoryResponse
from app.services.factory import ModelServiceFactory

router = APIRouter()


async def get_provider_or_404(provider_id: int, db: AsyncSession) -> ModelProvider:
    """Get provider or raise 404 error."""
    result = await db.execute(
        ModelProvider.__table__.select().where(ModelProvider.id == provider_id)
    )
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
    
    try:
        # Get model service
        service = await ModelServiceFactory.get_service(
            provider_id=provider.id,
            provider_name=provider.name,
            api_key=provider.api_key,
            config=provider.config
        )
        
        # Generate response
        response = await service.generate_response(request.message)
        
        # Save chat history
        chat_history = ChatHistory(
            model_provider_id=provider.id,
            user_message=request.message,
            assistant_message=response,
            metadata=request.metadata
        )
        db.add(chat_history)
        await db.commit()
        await db.refresh(chat_history)
        
        return chat_history
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
    
    try:
        # Get model service
        service = await ModelServiceFactory.get_service(
            provider_id=provider.id,
            provider_name=provider.name,
            api_key=provider.api_key,
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
                metadata=request.metadata
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
    
    result = await db.execute(
        ChatHistory.__table__.select()
        .where(ChatHistory.model_provider_id == provider_id)
        .order_by(ChatHistory.created_at.desc())
    )
    return result.scalars().all()
