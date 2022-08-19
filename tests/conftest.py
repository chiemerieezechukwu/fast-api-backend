import asyncio
import os
from copy import deepcopy
from unittest.mock import patch

import boto3
import factory
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from moto import mock_cognitoidp, mock_iam
from pytest_factoryboy import register

from app.db.models import User
from tests.common import USER_DATA
from tests.factories.user_factory import UserFactory
from tests.fake_urlopen import FakeUrlOpen

register(UserFactory)
user_data = factory.build(dict, FACTORY_CLASS=UserFactory)

os.environ["APP_ENV"] = "test"
os.environ["userpool__region"] = "eu-central-1"


def set_env_variables(userpool_id: str, app_client_id: str) -> None:
    os.environ["userpool__userpool_id"] = userpool_id
    os.environ["userpool__app_client_id"] = app_client_id


@pytest.fixture(scope="session")
@mock_iam
def cognito_client():
    cognito_client = boto3.client("cognito-idp")
    return cognito_client


@pytest.fixture
def apply_migrations(postgresql, cognito_user_auth, event_loop):
    import warnings

    import alembic
    from alembic.config import Config

    pg = postgresql.info

    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.dbname}"

    config = Config("alembic.ini")

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture(scope="session")
@mock_cognitoidp
def cognito_user_auth(cognito_client):
    fake_user_pool = cognito_client.create_user_pool(PoolName="test_pool")

    fake_user_pool_client = cognito_client.create_user_pool_client(
        UserPoolId=fake_user_pool["UserPool"]["Id"],
        ClientName="test_client",
        ExplicitAuthFlows=[
            "ALLOW_ADMIN_USER_PASSWORD_AUTH",
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
        ],
        ReadAttributes=[
            "full_name",
            "bio",
            "username",
            "email_verified",
            "cognito:username",
            "iat",
        ],
    )

    def prepare_user_attributes(local_user_data: dict) -> list:
        user_attributes = []
        local_user_data.update(
            {
                "email_verified": "True",
                "cognito:username": local_user_data["username"],
                "iat": "1588888888",
            }
        )
        for key, value in local_user_data.items():
            user_attributes.append({"Name": key, "Value": value})
        return user_attributes

    local_user_data = deepcopy(USER_DATA)
    app_client_id = fake_user_pool_client["UserPoolClient"]["ClientId"]
    userpool_id = fake_user_pool["UserPool"]["Id"]

    set_env_variables(userpool_id, app_client_id)

    cognito_client.sign_up(
        ClientId=app_client_id,
        Username=local_user_data["username"],
        Password="test_P4ssword",
        UserAttributes=prepare_user_attributes(local_user_data),
    )

    cognito_client.admin_confirm_sign_up(
        UserPoolId=userpool_id,
        Username=local_user_data["username"],
    )

    user_auth = cognito_client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": local_user_data["username"],
            "PASSWORD": "test_P4ssword",
        },
    )

    return user_auth["AuthenticationResult"]


@pytest.fixture
@mock_cognitoidp
def app(apply_migrations, event_loop) -> FastAPI:
    import requests

    jwk_url = "https://cognito-idp.fake_region.amazonaws.com/fake_userpool_id/.well-known/jwks.json"
    fake_jwk_response = requests.get(jwk_url).json()

    with patch("urllib.request.urlopen", return_value=FakeUrlOpen(return_value=fake_jwk_response)):
        from app.main import get_application

        return get_application()


@pytest.fixture
def unauthorized_client(enable_network, app: FastAPI) -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def authorized_client(unauthorized_client, cognito_user_auth):
    id_token = cognito_user_auth["IdToken"]
    unauthorized_client.headers = {"Authorization": f"Bearer {id_token}"}
    yield unauthorized_client


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_user(app: FastAPI, event_loop) -> User:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    from app.db.repositories.users import UsersRepository

    engine = app.state.db

    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True, future=True)

    # async with async_session() as session:
    #     result = await UsersRepository(session).create_user(**USER_DATA)

    session = async_session()

    try:
        result = await UsersRepository(session).create_user(**USER_DATA)
        return result
    except Exception as e:
        print("Error:t", e)
    finally:
        await session.close()
