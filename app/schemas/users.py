from typing import Optional

from pydantic import EmailStr

from app.schemas.rwschema import RWSchema


class UserInCreate(RWSchema):
    full_name: str
    username: str
    email: EmailStr


class UserInResponse(RWSchema):
    full_name: str
    username: str
    email: EmailStr
    bio: str = ""
    image: Optional[str]


class UserInUpdate(RWSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    image: Optional[str] = None
