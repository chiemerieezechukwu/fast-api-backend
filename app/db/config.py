from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()


class BaseModelOrm(Base):
    __abstract__ = True


async def ping_db(db: AsyncEngine) -> None:
    async with db.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def get_db(db_url: str) -> AsyncEngine:
    db = create_async_engine(db_url, future=True, echo=True, pool_pre_ping=True)

    # test db connection
    await ping_db(db)

    return db
