from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.models import BaseModelOrm
from app.db.models.common import DateTimeModelMixin


class Score(BaseModelOrm, DateTimeModelMixin):
    __tablename__ = "scores"

    score = Column(Integer)
    scorer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))

    def __repr__(self) -> str:
        return "<Score %s>" % self.id
