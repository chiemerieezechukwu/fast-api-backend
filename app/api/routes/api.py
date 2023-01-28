from fastapi import APIRouter

from app.api.routes import matches, tournaments, users

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(matches.router, prefix="/matches", tags=["matches"])
router.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])
