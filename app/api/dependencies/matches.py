from uuid import UUID

from fastapi import Depends, HTTPException
from starlette import status

from app.api.dependencies.authentication import get_current_authorized_user
from app.api.dependencies.database import get_repository
from app.db.errors import EntityDoesNotExist
from app.db.models import Match, MatchConfirmation, User
from app.db.repositories.match_confirmations import MatchConfirmationsRepository
from app.db.repositories.matches import MatchesRepository
from app.resources import strings
from app.services.matches import (
    check_match_can_be_modified,
    check_no_match_confirmation_exists,
    check_user_can_modify_match,
    check_user_comfirmed_match,
)


async def get_match_by_slug_from_path(
    slug: UUID,
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> Match:
    try:
        return await matches_repo.get_match_by_slug(slug=slug)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.MATCH_DOES_NOT_EXIST_ERROR,
        )


async def get_match_confirmations_from_match(
    match: Match = Depends(get_match_by_slug_from_path),
    match_confirmations_repo: MatchConfirmationsRepository = Depends(
        get_repository(MatchConfirmationsRepository),
    ),
) -> list[MatchConfirmation]:
    return await match_confirmations_repo.get_match_confirmations_by_match(match=match)


async def get_match_players_by_match_slug_from_path(
    slug: UUID,
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> list[User]:
    try:
        return await matches_repo.get_players_from_match_by_slug(slug=slug)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.UNAUTHORIZED_TO_UPDATE_MATCH,
        )


def check_match_update_permissions(
    match_players: list[User] = Depends(get_match_players_by_match_slug_from_path),
    current_user: User = Depends(get_current_authorized_user()),
) -> None:
    if not check_user_can_modify_match(match_players=match_players, current_user=current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.UNAUTHORIZED_TO_UPDATE_MATCH,
        )


def check_match_is_modifiable(
    match_confirmations: list[MatchConfirmation] = Depends(
        get_match_confirmations_from_match,
    ),
) -> None:
    if not check_match_can_be_modified(match_confirmations=match_confirmations):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.MATCH_IS_NOT_MODIFIABLE,
        )


def check_current_user_can_confirm_or_reject_match(
    match_confirmations: list[MatchConfirmation] = Depends(
        get_match_confirmations_from_match,
    ),
    current_user: User = Depends(get_current_authorized_user()),
) -> None:
    if check_no_match_confirmation_exists(match_confirmations=match_confirmations):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.NO_SCORES_TO_CONFIRM_REJECT,
        )

    if check_user_comfirmed_match(match_confirmations=match_confirmations, current_user=current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.USER_CONFIRMATION_ALREADY_EXISTS,
        )
