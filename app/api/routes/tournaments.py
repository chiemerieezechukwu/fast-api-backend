from fastapi import APIRouter, Depends, Path

from app.api.dependencies.database import get_repository
from app.db.repositories import TournamentsRepository
from app.schemas.matches import ListOfMatchesInResponse
from app.schemas.tournaments import TournamentInResponse

router = APIRouter()


# get all matches in tournament
@router.get(
    "/{slug}",
    response_model=ListOfMatchesInResponse,
    name="tournament:get-matches-in-tournament",
)
async def get_matches_in_tournament(
    slug: str = Path(min_length=1),
    # tournament_repo: TournamentsRepository = Depends(get_repository(TournamentsRepository)),
) -> ListOfMatchesInResponse:
    pass


# get tournamnents
@router.get(
    "",
    response_model=list[TournamentInResponse],
    name="tournaments:get-tournaments",
)
async def get_tournaments(
    tournament_repo: TournamentsRepository = Depends(get_repository(TournamentsRepository)),
) -> list[TournamentInResponse]:
    pass
