from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.models.models import ModelProvider
from app.schemas.schemas import ModelProviderCreate, ModelProviderInDB, ModelProviderUpdate
from app.services.factory import ModelServiceFactory

router = APIRouter()


@router.post("/", response_model=ModelProviderInDB)
async def create_provider(
    provider: ModelProviderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new model provider."""
    try:
        # Validate the provider by initializing the service
        await ModelServiceFactory.get_service(
            provider_id=-1,  # Temporary ID for validation
            provider_name=provider.name,
            api_key=provider.api_key,
            config=provider.config
        )
        
        # Check for existing provider with the same name
        from sqlalchemy import select
        stmt = select(ModelProvider).where(ModelProvider.name == provider.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"Provider with name '{provider.name}' already exists.")
        
        # Create provider in database
        db_provider = ModelProvider(
            name=provider.name,
            api_key=provider.api_key,
            config=provider.config
        )
        db.add(db_provider)
        await db.commit()
        await db.refresh(db_provider)
        
        return db_provider
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ModelProviderInDB])
async def list_providers(
    db: AsyncSession = Depends(get_db)
):
    """List all model providers."""
    from sqlalchemy import select
    stmt = select(ModelProvider).order_by(ModelProvider.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{provider_id}", response_model=ModelProviderInDB)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific model provider."""
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.put("/{provider_id}", response_model=ModelProviderInDB)
async def update_provider(
    provider_id: int,
    provider_update: ModelProviderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a model provider."""
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    db_provider = result.scalar_one_or_none()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Update provider fields
    for field, value in provider_update.dict(exclude_unset=True).items():
        setattr(db_provider, field, value)

    try:
        # Validate the updated provider
        await ModelServiceFactory.get_service(
            provider_id=provider_id,
            provider_name=db_provider.name,
            api_key=db_provider.api_key,
            config=db_provider.config
        )
        
        await db.commit()
        await db.refresh(db_provider)
        
        return db_provider
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a model provider."""
    from sqlalchemy import select
    stmt = select(ModelProvider).where(ModelProvider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    await db.delete(provider)
    await db.commit()
    
    # Remove service instance if it exists
    ModelServiceFactory.remove_service(provider_id)
    
    return {"message": "Provider deleted successfully"}
