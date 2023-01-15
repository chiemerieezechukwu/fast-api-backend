import asyncio
import os
from copy import deepcopy
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import boto3
import factory
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from moto import mock_cognitoidp
from pytest_factoryboy import register

from app.db.models import User
from tests.factories.user_factory import UserFactory
from tests.fake_urlopen import FakeUrlOpen

register(UserFactory)

os.environ["APP_ENV"] = "test"
os.environ["userpool__region"] = "eu-central-1"


@pytest.fixture
def apply_migrations(postgresql, cognito_user, enable_network):

    import alembic
    from alembic.config import Config

    pg = postgresql.info

    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.dbname}"

    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture(scope="session")
@mock_cognitoidp
def cognito_user():
    cognito_client = boto3.client("cognito-idp")
    fake_user_pool = cognito_client.create_user_pool(PoolName="test_pool")

    fake_user_pool_client = cognito_client.create_user_pool_client(
        UserPoolId=fake_user_pool["UserPool"]["Id"],
        ClientName="test_client",
        ExplicitAuthFlows=["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        ReadAttributes=["full_name", "bio", "username", "email_verified", "cognito:username", "iat"],
    )

    # return fake_user_pool, fake_user_pool_client, cognito_client

    def _prepare_user_attributes(user_data: dict) -> list:
        user_data_copy = deepcopy(user_data)
        user_data_copy.update(
            {
                "email_verified": "True",
                "cognito:username": user_data_copy["username"],
                "iat": "1588888888",
            }
        )

        return [{"Name": key, "Value": value} for key, value in user_data_copy.items()]

    user_data = factory.build(dict, FACTORY_CLASS=UserFactory)

    app_client_id = fake_user_pool_client["UserPoolClient"]["ClientId"]
    userpool_id = fake_user_pool["UserPool"]["Id"]

    os.environ["userpool__userpool_id"] = userpool_id
    os.environ["userpool__app_client_id"] = app_client_id

    cognito_client.sign_up(
        ClientId=app_client_id,
        Username=user_data["username"],
        Password="test_P4ssword",
        UserAttributes=_prepare_user_attributes(user_data),
    )

    cognito_client.admin_confirm_sign_up(
        UserPoolId=userpool_id,
        Username=user_data["username"],
    )

    user_auth = cognito_client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": user_data["username"],
            "PASSWORD": "test_P4ssword",
        },
    )

    return user_data, user_auth["AuthenticationResult"]


@pytest.fixture
@mock_cognitoidp
def app(apply_migrations) -> FastAPI:
    import requests

    jwk_url = "https://cognito-idp.fake_region.amazonaws.com/fake_userpool_id/.well-known/jwks.json"
    fake_jwk_response = requests.get(jwk_url).json()

    with patch("urllib.request.urlopen", return_value=FakeUrlOpen(return_value=fake_jwk_response)):
        from app.main import get_application

        app = get_application()
        engine: AsyncEngine = create_async_engine(os.getenv("DATABASE_URL"), future=True)
        app.state.db = engine

        return app


@pytest.fixture
def db_session(enable_network, app: FastAPI) -> AsyncSession:
    engine: AsyncEngine = app.state.db
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True, future=True)

    return async_session()


@pytest.fixture
async def unauthorized_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def authorized_client(unauthorized_client, cognito_user):
    id_token = cognito_user[1]["IdToken"]
    unauthorized_client.headers = {"Authorization": f"Bearer {id_token}"}
    yield unauthorized_client
