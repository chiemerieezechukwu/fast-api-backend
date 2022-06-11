from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.settings.app import AppSettings


async def ping_db(db: AsyncEngine) -> None:
    async with db.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def get_db(settings: AppSettings) -> AsyncEngine:
    db_url = settings.database_url
    echo = settings.debug
    db = create_async_engine(db_url, future=True, echo=echo, pool_pre_ping=True)

    # test db connection
    await ping_db(db)

    return db
