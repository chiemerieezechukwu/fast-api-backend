from typing import Optional

from pydantic import EmailStr, HttpUrl

from app.schemas.rwschema import RWSchema


class UserInLogin(RWSchema):
    email: EmailStr


class UserInCreate(UserInLogin):
    full_name: str
    username: str


class UserInResponse(RWSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None
