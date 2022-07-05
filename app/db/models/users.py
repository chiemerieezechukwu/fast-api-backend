from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import backref, relationship

from app.db.models import BaseModelOrm
from app.db.models.common import DateTimeModelMixin
from app.db.models.user_match_association import assoc_users_matches
from app.db.models.user_tournament_association import assoc_users_tournaments


class User(BaseModelOrm, DateTimeModelMixin):
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    image = Column(String, default="default.png")
    bio = Column(String, default="")
    is_active = Column(Boolean, default=False)

    scores = relationship("Score", backref="scorer", lazy="dynamic")
    tournaments_created = relationship("Tournament", backref="creator", lazy="dynamic")
    matches_created = relationship("Match", backref="creator", lazy="dynamic")
    match_confirmations = relationship("MatchConfirmation", backref="confirmed_by", lazy="dynamic")
    matches = relationship(
        "Match",
        secondary=assoc_users_matches,
        backref=backref("players", lazy="dynamic"),
        lazy="dynamic",
    )
    tournaments_joined = relationship(
        "Tournament",
        secondary=assoc_users_tournaments,
        backref=backref("participants", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return "<User %s>" % self.email
