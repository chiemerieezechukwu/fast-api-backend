from typing import Optional
from app.schemas.rwschema import RWSchema
from pydantic import EmailStr, HttpUrl


class UserInLogin(RWSchema):
    email: EmailStr
    password: str


class UserInCreate(UserInLogin):
    full_name: str
    username: str


class UserInResponse(RWSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None
