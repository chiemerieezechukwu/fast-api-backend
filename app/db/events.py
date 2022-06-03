from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings
from app.db.config import get_db


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Checking PostgreSQL connection")

    app.state.db = await get_db(settings)

    logger.info("PostgreSQL is connectable")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.db.dispose()

    logger.info("Connection closed")
