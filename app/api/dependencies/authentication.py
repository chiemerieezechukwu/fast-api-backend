import json
import urllib.request
from functools import lru_cache
from typing import Callable

from fastapi import Depends, HTTPException, Security
from loguru import logger
from starlette import status

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.db.errors import EntityDoesNotExist
from app.db.models import User
from app.db.repositories.users import UsersRepository
from app.resources import strings
from app.resources.cognito_auth import CognitoBearer
from app.schemas.cognito_auth import JWKS, CognitoClaims


@lru_cache(maxsize=1)
def _get_jwks() -> JWKS:
    settings: AppSettings = get_app_settings()
    keys_url = settings.userpool.get_jwk_key_url()
    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
        keys = json.loads(response.decode("utf-8"))

    return JWKS(**keys)


def get_current_authorized_user() -> Callable:
    return _get_current_user


def _auth_required() -> Callable:
    return CognitoBearer(jwks=_get_jwks(), settings=get_app_settings())


async def _get_current_user(
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    cognito_claims: CognitoClaims = Security(_auth_required()),
) -> User:

    try:
        return await users_repo.get_user_by_email(email=cognito_claims.email)
    except EntityDoesNotExist as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
        )
