from sqlalchemy import and_, select
from sqlalchemy.engine.result import Result

from app.db.models import Match, Score, User
from app.db.repositories.base import BaseRepository


class ScoresRepository(BaseRepository):
    async def create_score(self, *, match: Match, scorer: User) -> Score:
        score = Score(match=match, scorer=scorer)
        self.async_session.add(score)
        return score

    async def update_score(self, *, score: Score, score_value: int) -> Score:
        score.score = score_value
        return score

    async def get_score_by_match_and_scorer(self, *, match: Match, scorer: User) -> Score:
        q = select(Score).where(and_(Score.match_id == match.id, Score.scorer_id == scorer.id))
        result: Result = await self.async_session.execute(q)
        score = result.scalar_one_or_none()
        return score
