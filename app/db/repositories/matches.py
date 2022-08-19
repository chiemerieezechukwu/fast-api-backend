from sqlalchemy import and_, select
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.errors import EntityDoesNotExist
from app.db.models import Match, User
from app.db.models.match_confirmation import MatchConfirmation
from app.db.models.scores import Score
from app.db.repositories.base import BaseRepository
from app.db.repositories.match_confirmations import MatchConfirmationsRepository
from app.db.repositories.scores import ScoresRepository
from app.db.repositories.users import UsersRepository
from app.schemas.matches import MatchInUpdate


class MatchesRepository(BaseRepository):
    def __init__(self, async_session: AsyncSession) -> None:
        super().__init__(async_session)
        self._users_repo = UsersRepository(async_session)
        self._scores_repo = ScoresRepository(async_session)
        self._match_confirmations_repo = MatchConfirmationsRepository(async_session)

    async def create_match(
        self,
        *,
        current_user: User,
        opponent_email: str,
    ) -> Match:
        match = Match(creator=current_user)
        self.async_session.add(match)

        opponent = await self._users_repo.get_user_by_email(email=opponent_email)
        match.players.append(current_user)
        match.players.append(opponent)

        await self.__add_default_scores_to_match(
            match=match,
            current_user=current_user,
            opponent=opponent,
        )

        await self.__add_default_confirmations_to_match(
            match=match,
            current_user=current_user,
            opponent=opponent,
        )

        await self.async_session.commit()
        return match

    async def get_match_by_slug(self, *, slug: str) -> list[Row]:
        q = select(Match).where(Match.id == slug)
        result = await self.async_session.execute(q)
        match = result.scalar_one_or_none()

        if match:
            return match

        raise EntityDoesNotExist(f"match with slug {slug} does not exist")

    async def get_match_details_by_slug(self, *, slug: str) -> list[Row]:
        q = (
            select(User, Score, MatchConfirmation, Match)
            .select_from(User)
            .join(Score)
            .join(MatchConfirmation)
            .join(Match)
            .where(and_(MatchConfirmation.match_id == slug, Score.match_id == slug))
        )
        result = await self.async_session.execute(q)
        result = result.all()

        return result

    async def get_players_from_match_by_slug(self, *, slug: str) -> list[User]:
        match = await self.get_match_by_slug(slug=slug)
        result = await self.async_session.execute(match.players)
        result = result.scalars().all()
        return result

    async def get_matches_by_user(self, *, user: User) -> list[Match]:
        q = select(Match).where(Match.players.contains(user))
        result = await self.async_session.execute(q)
        matches = result.scalars().all()
        return matches

    async def update_match_scores(
        self,
        *,
        match: Match,
        current_user: User,
        match_update_data: list[MatchInUpdate],
    ) -> list[Row]:

        for player_match_update_data in match_update_data:
            player = await self._users_repo.get_user_by_email(email=player_match_update_data.score_by)

            if player_match_update_data.score is not None:
                await self._scores_repo.update_score(
                    score=await self._scores_repo.get_score_by_match_and_scorer(match=match, scorer=player),
                    score_value=player_match_update_data.score,
                )

        # add current_user's match confirmation
        await self.update_match_confirmation(
            match=match,
            current_user=current_user,
            is_confirmed=True,
        )

        await self.async_session.commit()
        return await self.get_match_details_by_slug(slug=match.id)

    async def update_match_confirmation(
        self,
        *,
        match: Match,
        current_user: User,
        is_confirmed: bool,
    ) -> None:
        await self._match_confirmations_repo.update_match_confirmation(
            match_confirmation=await self._match_confirmations_repo.get_match_confirmation_by_match_and_player(
                match=match,
                player=current_user,
            ),
            is_confirmed=is_confirmed,
        )

        await self.async_session.commit()

    async def reset_match_confirmations(self, *, match: Match) -> None:
        match_confirmations = await self._match_confirmations_repo.get_match_confirmations_by_match(
            match=match,
        )

        for match_confirmation in match_confirmations:
            await self._match_confirmations_repo.update_match_confirmation(
                match_confirmation=match_confirmation,
                is_confirmed=None,
            )

        await self.async_session.commit()

    async def __add_default_scores_to_match(
        self,
        *,
        match: Match,
        current_user: User,
        opponent: str,
    ) -> None:
        await self._scores_repo.create_score(match=match, scorer=current_user)
        await self._scores_repo.create_score(match=match, scorer=opponent)

    async def __add_default_confirmations_to_match(
        self,
        *,
        match: Match,
        current_user: User,
        opponent: User,
    ) -> None:
        await self._match_confirmations_repo.create_match_confirmation(
            match=match,
            confirmed_by=current_user,
        )
        await self._match_confirmations_repo.create_match_confirmation(
            match=match,
            confirmed_by=opponent,
        )
