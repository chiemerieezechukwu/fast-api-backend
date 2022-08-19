from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.match_confirmations import MatchConfirmationInResponse
from app.schemas.rwschema import RWSchema
from app.schemas.scores import ScoreInResponse
from app.schemas.users import UserInResponse


class MatchInCreate(RWSchema):
    opponent_email: EmailStr


class MatchInUpdate(RWSchema):
    score: int
    score_by: EmailStr


class ListOfMatchInUpdate(RWSchema):
    score_data: list[MatchInUpdate] = Field(min_items=2, max_items=2, unique_items=True)


class MatchInResponse(RWSchema):
    id: UUID = Field(alias="match_slug")

    class Config(RWSchema.Config):
        allow_population_by_field_name = True


class ListOfMatchesInResponse(RWSchema):
    matches: list[MatchInResponse]
    matches_count: int


class MatchInResponseWithDetails(RWSchema):
    User: UserInResponse = Field(alias="player")
    Score: ScoreInResponse = Field(alias="score")
    MatchConfirmation: MatchConfirmationInResponse = Field(alias="match_confirmation")
    is_match_creator: bool = Field(default=False)

    class Config(RWSchema.Config):
        allow_population_by_field_name = True
