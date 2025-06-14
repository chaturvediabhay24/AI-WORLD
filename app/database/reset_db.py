from app.models import models
from app.database.base import engine
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncio

async def drop_and_create_all():
    if isinstance(engine, AsyncEngine):
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.drop_all)
            await conn.run_sync(models.Base.metadata.create_all)
    else:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    asyncio.run(drop_and_create_all())
