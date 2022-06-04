from sqlalchemy import Boolean, Column, String

from app.db.config import BaseModelOrm
from app.db.models.common import DateTimeModelMixin, IDModelMixin


class User(BaseModelOrm, DateTimeModelMixin, IDModelMixin):
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
