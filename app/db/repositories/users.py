from typing import Optional

from sqlalchemy import select
from sqlalchemy.engine.result import Result

from app.db.errors import EntityDoesNotExist
from app.db.models import User
from app.db.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    async def get_user_by_email(self, *, email: str) -> User:
        q = select(User).where(User.email == email)
        result: Result = await self.async_session.execute(q)
        # TODO: Check the exception type
        user = result.scalars().one_or_none()

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

    async def update_user(
        self,
        *,
        user: User,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        email: Optional[str] = None,
        image: Optional[str] = None,
    ) -> User:
        user.full_name = full_name or user.full_name
        user.username = username or user.username
        user.email = email or user.email
        user.image = image or user.image
        user.bio = bio or user.bio

        await self.async_session.commit()
        return user
