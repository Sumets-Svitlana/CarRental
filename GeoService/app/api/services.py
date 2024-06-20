from fastapi import Depends
import redis.asyncio as redis

from app.api.schemas import StationCreatingSchema, StationSchema, StationUpdatingSchema
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.storage.redis_client import get_redis_client, STATION_STORAGE


class StationService:
    def __init__(self, redis_client: redis.Redis = Depends(get_redis_client)):
        self.redis_client = redis_client
        self.storage = STATION_STORAGE

    async def get_stations(self) -> list[StationSchema]:
        keys = await self.redis_client.hkeys(self.storage)
        if not keys:
            return []

        stations = await self.redis_client.hmget(self.storage, keys)
        return [StationSchema.model_validate_json(station) for station in stations]

    async def get_station(self, station_id: str) -> StationSchema:
        station = await self.redis_client.hget(self.storage, station_id)
        if not station:
            raise NotFoundError(status_code=404, message=f'Station {station_id} not found')

        return StationSchema.model_validate_json(station)

    async def create_station(self, creating_schema: StationCreatingSchema) -> StationSchema:
        if await self.redis_client.hexists(self.storage, str(creating_schema.station_id)):
            raise AlreadyExistsError(status_code=400, message=f'Station {creating_schema.station_id} already exists')
        await self.redis_client.hset(self.storage, str(creating_schema.station_id), creating_schema.model_dump_json())
        return StationSchema.model_validate(creating_schema)

    async def update_station(self, station_id: str, updating_schema: StationUpdatingSchema) -> StationSchema:
        if not await self.redis_client.hexists(self.storage, station_id):
            raise NotFoundError(status_code=404, message=f'Station {station_id} not found')

        station = StationSchema(station_id=station_id, **updating_schema.model_dump())
        await self.redis_client.hset(self.storage, station_id, station.model_dump_json())

        return station

    async def delete_station(self, station_id: str):
        if not await self.redis_client.hexists(self.storage, station_id):
            raise NotFoundError(status_code=404, message=f'Station {station_id} not found')

        await self.redis_client.hdel(self.storage, station_id)
