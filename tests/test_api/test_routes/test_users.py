import factory
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from moto import mock_cognitoidp
from sqlalchemy import select

from app.db.models import User
from tests.factories.user_factory import UserFactory

pytestmark = pytest.mark.asyncio

# # @pytest.fixture
# async def test_user(db_session, cognito_user) -> User:

#     user_data, *_ = cognito_user
#     user = User(**user_data)
#     db_session.add(user)
#     await db_session.commit()

#     # q = select(User).where(User.email == user_data["email"])
#     # result = await db_session.execute(q)
#     # return result.scalars().first()

#     return user


async def test_can_register_user(app: FastAPI, userpool_user, async_client: AsyncClient, monkeypatch):
    user_data = userpool_user["user_data"]
    response = await async_client.post(app.url_path_for("users:register"), json={"user": user_data})

    assert response.status_code == 201
    assert all(user_data[key] == response.json()[key] for key in user_data.keys())

    # test can't register duplicate user with same email
    response = await async_client.post(app.url_path_for("users:register"), json={"user": user_data})
    assert response.status_code == 400

    # test can't register user with invalid email
    response = await async_client.post(
        app.url_path_for("users:register"), json={"user": {**user_data, "email": "invalid_email"}}
    )
    assert response.status_code == 422

    # test can't register user with empty body
    response = await async_client.post(app.url_path_for("users:register"), json={"user": {}})
    assert response.status_code == 422

    id_token = userpool_user["user_auth"]["IdToken"]
    print(id_token)
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {id_token}"})
    response = await async_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == 200


async def test_can_get_current_user(async_client: AsyncClient, app: FastAPI, monkeypatch, userpool_user) -> None:
    id_token = userpool_user["user_auth"]["IdToken"]
    print(id_token)
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {id_token}"})
    response = await async_client.get(app.url_path_for("users:get-current-user"))

    print(response.json())

    assert response.status_code == 404


# # async def test_bla(authorized_client, app, test_user):
# #     response = authorized_client.get(app.url_path_for("users:get-current-user"))

# # assert response.json() == test_user


async def test_try(userpool_user, db_session):

    # save the user to the database
    user_data = userpool_user["user_data"]
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()

    # query the user from the database
    q = select(User).where(User.email == user_data["email"])
    result = await db_session.execute(q)
    user = result.scalars().first()

    # assert the user is the same
    assert user.email == user_data["email"]
