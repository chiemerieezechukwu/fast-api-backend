from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.api.dependencies.authentication import get_current_authorized_user
from app.api.dependencies.database import get_repository
from app.db.models import User
from app.db.repositories.users import UsersRepository
from app.resources import strings
from app.schemas.users import UserInCreate, UserInResponse, UserInUpdate
from app.services.users import check_email_is_taken

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    response_model=UserInResponse,
    name="users:register",
)
async def register(
    user_create: UserInCreate = Body(embed=True, alias="user"),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserInResponse:
    if await check_email_is_taken(users_repo, user_create.email):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.EMAIL_TAKEN,
        )

    user = await users_repo.create_user(**user_create.dict())

    return UserInResponse.from_orm(user)


@router.get("/me", response_model=UserInResponse, name="users:get-current-user")
async def get_current_user(
    current_user: User = Depends(get_current_authorized_user()),
) -> UserInResponse:
    return UserInResponse.from_orm(current_user)


@router.put("/me", response_model=UserInResponse, name="users:update-current-user")
async def update_current_user(
    user_update: UserInUpdate = Body(embed=True, alias="user"),
    current_user: User = Depends(get_current_authorized_user()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserInResponse:
    if user_update.email and user_update.email != current_user.email:
        if await check_email_is_taken(users_repo, user_update.email):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=strings.EMAIL_TAKEN,
            )

    user = await users_repo.update_user(user=current_user, **user_update.dict())

    return UserInResponse.from_orm(user)
