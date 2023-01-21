import factory
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from tests.factories.user_factory import UserFactory

pytestmark = pytest.mark.asyncio


async def test_register_user(app: FastAPI, async_client: AsyncClient):
    user_data = factory.build(dict, FACTORY_CLASS=UserFactory)
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


async def test_can_get_current_user(async_client: AsyncClient, app: FastAPI, monkeypatch, current_user) -> None:
    id_token = current_user["auth"]["IdToken"]
    monkeypatch.setattr(async_client, "headers", {"Authorization": f"Bearer {id_token}"})
    response = await async_client.get(app.url_path_for("users:get-current-user"))

    print(response.json())

    assert response.status_code == 200
