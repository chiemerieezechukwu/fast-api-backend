from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.models import BaseModelOrm
from app.db.models.common import DateTimeModelMixin


class MatchConfirmation(BaseModelOrm, DateTimeModelMixin):
    __tablename__ = "match_confirmations"

    is_confirmed = Column(Boolean)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return "<MatchConfirmation %s>" % self.id
