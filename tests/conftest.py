import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.models import ModelProvider, ChatHistory


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_db):
    """Get a test database session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def test_provider(db_session):
    """Create a test model provider."""
    provider = ModelProvider(
        name="test_openai",
        api_key="test-key",
        config={
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider


@pytest_asyncio.fixture
async def test_chat_history(db_session, test_provider):
    """Create a test chat history entry."""
    chat = ChatHistory(
        model_provider_id=test_provider.id,
        user_message="Hello",
        assistant_message="Hi there!",
        metadata={"test": True}
    )
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)
    return chat
