from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from app.db.models import BaseModelOrm

assoc_users_tournaments = Table(
    "assoc_users_tournaments",
    BaseModelOrm.metadata,
    Column("player_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("tournament_id", UUID(as_uuid=True), ForeignKey("tournaments.id")),
)
