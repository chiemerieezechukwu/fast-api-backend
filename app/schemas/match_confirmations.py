from typing import Optional

from app.schemas.rwschema import RWSchema


class MatchConfirmationInResponse(RWSchema):
    is_confirmed: Optional[bool] = None
