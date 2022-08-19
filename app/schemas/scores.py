from typing import Optional

from app.schemas.rwschema import RWSchema


class ScoreInResponse(RWSchema):
    score: Optional[int] = None
