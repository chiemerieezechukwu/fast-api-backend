from fastapi import APIRouter, Body, Depends, Path, Response
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.authentication import get_current_authorized_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.matches import (
    check_current_user_can_confirm_or_reject_match,
    check_match_is_modifiable,
    check_match_update_permissions,
    get_match_by_slug_from_path,
)
from app.db.models import Match, User
from app.db.repositories.matches import MatchesRepository
from app.schemas.matches import (
    ListOfMatchesInResponse,
    ListOfMatchInUpdate,
    MatchInCreate,
    MatchInResponse,
    MatchInResponseWithDetails,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    response_model=MatchInResponse,
    name="matches:create-match",
)
async def create(
    match_create: MatchInCreate = Body(embed=True, alias="match"),
    current_user: User = Depends(get_current_authorized_user()),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> MatchInResponse:
    match = await matches_repo.create_match(
        current_user=current_user,
        opponent_email=match_create.opponent_email,
    )

    return MatchInResponse.from_orm(match)


@router.get(
    "",
    response_model=ListOfMatchesInResponse,
    name="matches:get-matches-current-user",
)
async def get_matches_current_user(
    current_user: User = Depends(get_current_authorized_user()),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> ListOfMatchesInResponse:
    matches = await matches_repo.get_matches_by_user(user=current_user)
    matches_for_response = [MatchInResponse.from_orm(match) for match in matches]

    return ListOfMatchesInResponse(
        matches=matches_for_response,
        matches_count=len(matches),
    )


@router.get(
    "/{slug}",
    response_model=list[MatchInResponseWithDetails],
    name="matches:get-match-details",
)
async def get_match_details_by_slug(
    slug: str = Path(min_length=1),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> list[MatchInResponseWithDetails]:
    match_details_rows = await matches_repo.get_match_details_by_slug(slug=slug)

    return [
        MatchInResponseWithDetails.from_orm(match_details_row).copy(
            update={"is_match_creator": match_details_row.Match.creator == match_details_row.User}
        )
        for match_details_row in match_details_rows
    ]


@router.put(
    "/{slug}/scores",
    response_model=list[MatchInResponseWithDetails],
    name="matches:update-match-scores",
    dependencies=[
        Depends(check_match_update_permissions),
        Depends(check_match_is_modifiable),
    ],
)
async def update_match_scores(
    match_update: ListOfMatchInUpdate = Body(alias="match_update_data"),
    match: Match = Depends(get_match_by_slug_from_path),
    current_user: User = Depends(get_current_authorized_user()),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> list[MatchInResponseWithDetails]:
    match_details_rows = await matches_repo.update_match_scores(
        match=match,
        current_user=current_user,
        match_update_data=match_update.score_data,
    )

    return [
        MatchInResponseWithDetails.from_orm(match_details_row).copy(
            update={"is_match_creator": match_details_row.Match.creator == match_details_row.User}
        )
        for match_details_row in match_details_rows
    ]


@router.put(
    "/{slug}/confirm",
    name="matches:confirm-match-scores",
    dependencies=[
        Depends(check_match_update_permissions),
        Depends(check_current_user_can_confirm_or_reject_match),
    ],
    response_class=Response,
    status_code=HTTP_200_OK,
)
async def confirm_match_scores(
    match: Match = Depends(get_match_by_slug_from_path),
    current_user: User = Depends(get_current_authorized_user()),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> None:
    await matches_repo.update_match_confirmation(
        match=match,
        current_user=current_user,
        is_confirmed=True,
    )


@router.put(
    "/{slug}/reject",
    name="matches:reject-match-scores",
    dependencies=[
        Depends(get_current_authorized_user()),
        Depends(check_match_update_permissions),
        Depends(check_current_user_can_confirm_or_reject_match),
    ],
    response_class=Response,
    status_code=HTTP_200_OK,
)
async def reject_match_scores(
    match: Match = Depends(get_match_by_slug_from_path),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> None:
    await matches_repo.reset_match_confirmations(match=match)
