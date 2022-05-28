from fastapi import APIRouter, Body, Depends
from starlette.status import HTTP_201_CREATED

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.db.repositories.users import UsersRepository
from app.schemas.users import UserInCreate, UserInResponse

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    response_model=UserInResponse,
    name="user:register",
)
async def register(
    user_create: UserInCreate = Body(embed=True, alias="user"),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    settings: AppSettings = Depends(get_app_settings),
) -> UserInResponse:
    user = await users_repo.create_user(**user_create.dict())

    return user
