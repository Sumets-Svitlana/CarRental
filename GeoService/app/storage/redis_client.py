from functools import lru_cache

import redis.asyncio as redis

from app.core.config import settings

STATION_STORAGE = 'stations'


@lru_cache
def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
