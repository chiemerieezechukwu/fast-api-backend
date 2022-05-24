import logging

from pydantic import SecretStr

from app.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "Test FastAPI application"
    version: str = "Test version"

    secret_key: SecretStr = SecretStr("test_secret")

    allowed_hosts: list[str] = ["*"]

    logging_level: int = logging.DEBUG
