from sqlalchemy.engine.result import Result

from app.db.errors import EntityDoesNotExist
from app.db.models import User
from app.db.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    async def get_user_by_id(self, *, id: int) -> User:
        return await self.async_session.get(User, id)

    async def get_user_by_email(self, *, email: str) -> User:
        q = self.select(User).where(User.email == email)
        result: Result = await self.async_session.execute(q)
        user = result.scalars().first()

        if user:
            return user
        raise EntityDoesNotExist(f"user with email {email} does not exist")

    async def get_user_by_username(self, *, username: str) -> User:
        pass

    async def create_user(
        self,
        *,
        full_name: str,
        username: str,
        email: str,
    ) -> User:
        user = User(full_name=full_name, username=username, email=email)
        self.async_session.add(user)
        await self.async_session.commit()
        return user

    async def update_user(self, id, data):
        pass
