from app.db.models.match_confirmation import MatchConfirmation
from app.db.models.users import User


def check_user_can_modify_match(*, match_players: list[User], current_user: User) -> bool:
    return current_user in match_players


def check_match_can_be_modified(*, match_confirmations: list[MatchConfirmation]) -> bool:
    """
    If there's at least one match confirmation, the match can't be modified to add scores.
    """
    return not any(match_confirmation.is_confirmed for match_confirmation in match_confirmations)


def is_match_pending_confirmation(*, match_confirmations: list[MatchConfirmation]) -> bool:
    """
    If there's exactly one match confirmation that is `None`,
    then the match is pending confirmation.
    """
    count = 0
    for match_confirmation in match_confirmations:
        if match_confirmation.is_confirmed is None:
            count += 1
    return count == 1


def check_no_match_confirmation_exists(*, match_confirmations: list[MatchConfirmation]) -> bool:
    """
    If there are no match confirmations, then no scores has been proposed.
    """
    return all(match_confirmation.is_confirmed is None for match_confirmation in match_confirmations)


def check_user_comfirmed_match(*, match_confirmations: list[MatchConfirmation], current_user: User) -> bool:
    return any(
        match_confirmation.player_id == current_user.id
        for match_confirmation in match_confirmations
        if match_confirmation.is_confirmed is not None
    )
