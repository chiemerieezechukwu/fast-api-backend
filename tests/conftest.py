import asyncio
import os
from copy import deepcopy
from typing import Generator
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import BaseModelOrm

import boto3
import factory
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from moto import mock_cognitoidp
from pytest_factoryboy import register

from tests.factories.user_factory import UserFactory
from tests.fake_urlopen import FakeUrlOpen

register(UserFactory)

os.environ["APP_ENV"] = "test"
os.environ["userpool__region"] = "eu-central-1"
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def cognito_client():
    cognito_client = boto3.client("cognito-idp")
    return cognito_client


@pytest.fixture(scope="session")
@mock_cognitoidp
def userpool_user(cognito_client) -> dict:
    userpool = cognito_client.create_user_pool(PoolName="test_pool")

    userpool_client = cognito_client.create_user_pool_client(
        UserPoolId=userpool["UserPool"]["Id"],
        ClientName="test_client",
        ExplicitAuthFlows=["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        ReadAttributes=["full_name", "bio", "username", "email_verified", "cognito:username", "iat", "email"],
    )

    userpool_client_id = userpool_client["UserPoolClient"]["ClientId"]
    userpool_id = userpool_client["UserPoolClient"]["UserPoolId"]

    os.environ["userpool__userpool_id"] = userpool_id
    os.environ["userpool__app_client_id"] = userpool_client_id

    user_data: dict = factory.build(dict, FACTORY_CLASS=UserFactory)
    user_data_extended = {
        **user_data,
        "email_verified": "True",
        "cognito:username": user_data["username"],
        "iat": "123456789",
    }

    cognito_client.sign_up(
        ClientId=userpool_client_id,
        Username=user_data_extended["username"],
        Password="test_P4ssword",
        UserAttributes=[{"Name": key, "Value": value} for key, value in user_data_extended.items()],
    )

    cognito_client.admin_confirm_sign_up(UserPoolId=userpool_id, Username=user_data_extended["username"])

    user_auth = cognito_client.initiate_auth(
        ClientId=userpool_client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": user_data_extended["username"], "PASSWORD": "test_P4ssword"},
    )

    return {"user_data": user_data, "user_auth": user_auth["AuthenticationResult"]}


@pytest.fixture
@mock_cognitoidp
def app(override_get_session, userpool_user) -> FastAPI:
    import requests

    jwk_url = "https://cognito-idp.fake_region.amazonaws.com/fake_userpool_id/.well-known/jwks.json"
    fake_jwk_response = requests.get(jwk_url).json()

    with patch("urllib.request.urlopen", return_value=FakeUrlOpen(return_value=fake_jwk_response)):
        from app.api.dependencies.database import _get_session
        from app.main import get_application

        app = get_application()
        app.dependency_overrides[_get_session] = override_get_session

        return app


@pytest.fixture
async def db_session(enable_network, postgresql) -> AsyncSession:
    pg = postgresql.info
    db_url = f"postgresql+asyncpg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.dbname}"
    os.environ["DATABASE_URL"] = db_url

    engine: AsyncEngine = create_async_engine(db_url, future=True)
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModelOrm.metadata.drop_all)
        await conn.run_sync(BaseModelOrm.metadata.create_all)
        async with async_session(bind=conn) as session:

            yield session

            await session.flush()
            await session.rollback()


@pytest.fixture
def override_get_session(db_session: AsyncSession):
    async def _override_get_session():
        yield db_session

    return _override_get_session


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
