from functools import lru_cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.models.orders import Order


@lru_cache
async def __create_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(get_settings().DATABASE_URL)


async def connect_to_mongodb():
    client = await __create_mongo_client()
    await init_beanie(
        database=client.orders_db,
        document_models=[Order],
    )
