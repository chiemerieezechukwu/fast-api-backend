from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from app.db.models import BaseModelOrm

assoc_users_matches = Table(
    "assoc_users_matches",
    BaseModelOrm.metadata,
    Column("player_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("match_id", UUID(as_uuid=True), ForeignKey("matches.id")),
)
