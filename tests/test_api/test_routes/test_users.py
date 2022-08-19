import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.models import User
from tests.common import USER_DATA

pytestmark = pytest.mark.asyncio


async def test_can_register_user(unauthorized_client: TestClient, app: FastAPI):
    response = unauthorized_client.post(app.url_path_for("users:register"), json={"user": USER_DATA})

    assert response.status_code == 201
    return response.json()


async def test_can_get_current_user(authorized_client: TestClient, app: FastAPI, test_user: User) -> None:
    response = authorized_client.get(app.url_path_for("users:get-current-user"))

    print(test_user.full_name)

    assert response.status_code == 404


# async def test_bla(authorized_client, app, test_user):
#     response = authorized_client.get(app.url_path_for("users:get-current-user"))

# assert response.json() == test_user
