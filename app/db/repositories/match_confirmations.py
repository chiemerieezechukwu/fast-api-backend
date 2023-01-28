from sqlalchemy import and_, select

from app.db.models import Match, MatchConfirmation, User
from app.db.repositories.base import BaseRepository


class MatchConfirmationsRepository(BaseRepository):
    async def create_match_confirmation(
        self,
        *,
        match: Match,
        confirmed_by: User,
    ) -> MatchConfirmation:
        match_confirmation = MatchConfirmation(match=match, confirmed_by=confirmed_by)
        self.async_session.add(match_confirmation)
        return match_confirmation

    async def get_match_confirmations_by_match(self, *, match: Match) -> list[MatchConfirmation]:
        q = select(MatchConfirmation).where(MatchConfirmation.match_id == match.id)
        result = await self.async_session.execute(q)
        return result.scalars().all()

    async def update_match_confirmation(
        self,
        *,
        match_confirmation: MatchConfirmation,
        is_confirmed: bool,
    ) -> MatchConfirmation:
        match_confirmation.is_confirmed = is_confirmed
        return match_confirmation

    async def get_match_confirmation_by_match_and_player(
        self,
        *,
        match: Match,
        player: User,
    ) -> MatchConfirmation:
        q = select(MatchConfirmation).where(
            and_(
                MatchConfirmation.match_id == match.id,
                MatchConfirmation.player_id == player.id,
            )
        )
        result = await self.async_session.execute(q)
        return result.scalar_one_or_none()
