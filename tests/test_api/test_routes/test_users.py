import factory
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import User

# pytestmark = pytest.mark.asyncio


# @pytest.fixture
async def test_user(db_session, cognito_user) -> User:

    user_data, *_ = cognito_user
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()

    # q = select(User).where(User.email == user_data["email"])
    # result = await db_session.execute(q)
    # return result.scalars().first()

    return user


async def test_can_register_user(unauthorized_client: AsyncClient, app: FastAPI, cognito_user, authorized_client: AsyncClient):
    # user_data: dict = factory.build(dict, FACTORY_CLASS=UserFactory)
    user_data, _ = cognito_user
    response = await unauthorized_client.post(app.url_path_for("users:register"), json={"user": user_data})

    assert response.status_code == 201
    assert all(user_data[key] == response.json()[key] for key in user_data.keys())

    # test can't register duplicate user with same email
    response = await unauthorized_client.post(app.url_path_for("users:register"), json={"user": user_data})
    assert response.status_code == 400

    # test can't register user with invalid email
    response = await unauthorized_client.post(
        app.url_path_for("users:register"), json={"user": {**user_data, "email": "invalid_email"}}
    )
    assert response.status_code == 422

    # test can't register user with empty body
    response = await unauthorized_client.post(app.url_path_for("users:register"), json={"user": {}})
    assert response.status_code == 422

    response = await authorized_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == 200
    print(response.json())


# async def test_can_get_current_user(authorized_client: AsyncClient, app: FastAPI, cognito_user, test_user) -> None:
#     response = await authorized_client.get(app.url_path_for("users:get-current-user"))

#     # print(cognito_user, test_user)

#     assert response.status_code == 404


# async def test_bla(authorized_client, app, test_user):
#     response = authorized_client.get(app.url_path_for("users:get-current-user"))

# assert response.json() == test_user
