from sqlalchemy import Boolean, Column, String

from app.db.config import BaseModelOrm
from app.db.models.common import DateTimeModelMixin, IDModelMixin


class User(BaseModelOrm, DateTimeModelMixin, IDModelMixin):
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)

    def check_password(self, password: str) -> bool:
        pass

    def set_password(self, password: str) -> None:
        pass
