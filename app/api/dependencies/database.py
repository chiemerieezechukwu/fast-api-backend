from typing import AsyncGenerator, Callable, Type
from fastapi import Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine


def _create_session(
    engine: AsyncEngine,
) -> AsyncSession:
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )
    return AsyncSessionLocal()


async def _get_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = request.app.state.db
    async with _create_session(engine) as async_session:
        yield async_session


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[AsyncSession], BaseRepository]:
    def _get_repo(
        async_session: AsyncSession = Depends(_get_session),
    ) -> BaseRepository:
        return repo_type(async_session)

    return _get_repo
