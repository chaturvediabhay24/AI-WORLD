from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.get_database_url, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    id: Mapped[int]
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate tablename from class name."""
        return cls.__name__.lower()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
