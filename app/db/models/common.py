import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class DateTimeModelMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IDModelMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
