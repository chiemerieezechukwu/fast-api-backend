from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.common import BaseModelOrm, DateTimeModelMixin


class Tournament(BaseModelOrm, DateTimeModelMixin):
    __tablename__ = "tournaments"

    name = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    matches = relationship("Match", backref="tournament", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Tournament %s>" % self.id
