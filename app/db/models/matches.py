from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models import BaseModelOrm
from app.db.models.common import DateTimeModelMixin


class Match(BaseModelOrm, DateTimeModelMixin):
    __tablename__ = "matches"

    # determines that a match is part of a tournament if not null
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=True)
    match_creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    scores = relationship("Score", backref="match", lazy="dynamic")
    confirmations = relationship("MatchConfirmation", backref="match", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Match %s>" % self.id
