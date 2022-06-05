from typing import Callable, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from app.db.config import BaseModelOrm


class BaseRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    @property
    def async_session(self) -> AsyncSession:
        return self._async_session

    @property
    def select(self) -> Callable[[Type[BaseModelOrm]], Select]:
        return select
