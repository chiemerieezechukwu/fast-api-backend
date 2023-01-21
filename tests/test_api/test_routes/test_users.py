import factory
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from tests.factories.user_factory import UserFactory

pytestmark = pytest.mark.asyncio


@pytest.fixture
def user_data():
    return factory.build(dict, FACTORY_CLASS=UserFactory)


@pytest.fixture
def current_user_auth_token(current_user):
    return current_user["auth"]["IdToken"]


async def test_can_register_user(app: FastAPI, async_client: AsyncClient, user_data):
    response = await async_client.post(app.url_path_for("users:register"), json={"user": user_data})

    # assert that user is created and that the initial data is a subset of the response data
    assert response.status_code == 201
    assert all(user_data[key] == response.json()[key] for key in user_data.keys())


async def test_cannot_register_user_with_existing_email(
    app: FastAPI,
    async_client: AsyncClient,
    user_data,
    db_session,
    user,
    monkeypatch,
):
    db_session.add(user)
    await db_session.commit()

    monkeypatch.setitem(user_data, "email", user.email)

    response = await async_client.post(app.url_path_for("users:register"), json={"user": user_data})
    assert response.status_code == 400
    assert "errors" in response.json().keys()


async def test_cannot_register_user_with_invalid_data(app: FastAPI, async_client: AsyncClient, user_data):
    response = await async_client.post(
        app.url_path_for("users:register"), json={"user": {**user_data, "email": "invalid_email"}}
    )
    assert response.status_code == 422
    assert "errors" in response.json().keys()


async def test_cannot_register_user_with_empty_body(app: FastAPI, async_client: AsyncClient):
    response = await async_client.post(app.url_path_for("users:register"), json={"user": {}})
    assert response.status_code == 422
    assert "errors" in response.json().keys()


async def test_can_get_current_user(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    current_user_auth_token,
) -> None:
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {current_user_auth_token}"})

    response = await async_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == 200


async def test_cannot_get_current_user_without_authorization(async_client: AsyncClient, app: FastAPI, monkeypatch):
    monkeypatch.setattr(async_client, "headers", {})

    response = await async_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == 401
    assert "errors" in response.json().keys()


async def test_cannot_get_current_user_with_invalid_authorization(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
):
    monkeypatch.setattr(async_client, "headers", {"Authorization": "Bearer invalid_token"})

    response = await async_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == 401
    assert "errors" in response.json().keys()


async def test_can_update_current_user(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    current_user_auth_token,
    user_data,
) -> None:
    monkeypatch.setitem(user_data, "bio", "new bio")
    monkeypatch.setitem(user_data, "image", "https://fakeimage.com/image.png")
    monkeypatch.setitem(user_data, "email", "new_email@email.com")
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {current_user_auth_token}"})

    response = await async_client.put(app.url_path_for("users:update-current-user"), json={"user": user_data})
    assert response.status_code == 200
    assert response.json()["bio"] == user_data["bio"]
    assert response.json()["image"] == user_data["image"]
    assert response.json()["email"] == user_data["email"]


async def test_cannot_update_current_user_with_invalid_authorization(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    user_data,
):
    monkeypatch.setitem(user_data, "bio", "new bio")
    monkeypatch.setitem(user_data, "image", "https://fakeimage.com/image.png")
    monkeypatch.setitem(user_data, "email", "new_email@email.com")
    monkeypatch.setattr(async_client, "headers", {"Authorization": "Bearer invalid_token"})

    response = await async_client.put(app.url_path_for("users:update-current-user"), json={"user": user_data})
    assert response.status_code == 401
    assert "errors" in response.json().keys()


async def test_cannot_update_current_user_with_empty_authorization(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    user_data,
):
    monkeypatch.setitem(user_data, "bio", "new bio")
    monkeypatch.setitem(user_data, "image", "https://fakeimage.com/image.png")
    monkeypatch.setitem(user_data, "email", "new_email@email.com")
    monkeypatch.setattr(async_client, "headers", {})

    response = await async_client.put(app.url_path_for("users:update-current-user"), json={"user": user_data})
    assert response.status_code == 401
    assert "errors" in response.json().keys()


async def test_cannot_update_current_user_email_with_existing_email(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    db_session,
    user,
    current_user_auth_token,
    user_data,
):
    # save a user to db
    db_session.add(user)
    await db_session.commit()

    monkeypatch.setitem(user_data, "email", user.email)
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {current_user_auth_token}"})

    response = await async_client.put(app.url_path_for("users:update-current-user"), json={"user": user_data})
    assert response.status_code == 400


async def test_can_update_current_user_email_to_non_existing_email(
    async_client: AsyncClient,
    app: FastAPI,
    monkeypatch,
    current_user_auth_token,
    user_data,
):
    new_email = "new_email@email.com"
    monkeypatch.setitem(user_data, "email", new_email)
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {current_user_auth_token}"})

    response = await async_client.put(app.url_path_for("users:update-current-user"), json={"user": user_data})
    assert response.status_code == 200
    assert response.json()["email"] == new_email
