from fastapi import APIRouter, Body, Depends
from starlette.status import HTTP_201_CREATED

from app.api.dependencies.authentication import get_current_authorized_user
from app.api.dependencies.database import get_repository
from app.db.models.users import User
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
) -> UserInResponse:
    user = await users_repo.create_user(**user_create.dict())

    return UserInResponse(**vars(user))


@router.get("/me", name="user:me")
async def get_current_user(
    user: User = Depends(get_current_authorized_user()),
) -> UserInResponse:
    return UserInResponse(**vars(user))
