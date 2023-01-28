import logging

from app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True
    db_engine_echo: bool = True
    title: str = "Dev FastAPI application"
    version: str = "Dev version"

    allowed_hosts: list[str] = ["*"]

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
