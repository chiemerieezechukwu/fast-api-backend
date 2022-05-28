from app.db.models import User
from app.db.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    async def get_user_by_id(self, *, id: int):
        pass

    async def get_user_by_email(self, *, email: str):
        pass

    async def get_user_by_username(self, *, username: str):
        pass

    async def create_user(
        self,
        *,
        full_name: str,
        username: str,
        email: str,
        password: str,
    ) -> User:
        user = User(full_name=full_name, username=username)
        self.async_session.add(user)
        await self.async_session.commit()
        return user

    async def update_user(self, id, data):
        pass
