from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    @property
    def async_session(self) -> AsyncSession:
        return self._async_session
