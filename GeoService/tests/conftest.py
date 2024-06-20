from typing import AsyncIterator

import fakeredis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.schemas import StationCreatingSchema, StationUpdatingSchema, WorkingHoursSchema
from app.core.enums import Weekday
from app.storage.redis_client import get_redis_client

TEST_HOST = 'http://test'


@pytest.fixture(scope='session')
async def app() -> FastAPI:
    from app.main import create_app

    _app = create_app()

    yield _app


@pytest.fixture
async def redis_client(app):
    redis_session = fakeredis.FakeAsyncRedis(decode_responses=True)

    async def _get_async_redis_session() -> AsyncIterator[fakeredis.FakeAsyncRedis]:
        yield redis_session

    app.dependency_overrides[get_redis_client] = _get_async_redis_session
    yield redis_session


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client


@pytest.fixture
async def valid_test_station_json_data() -> dict:
    return {
        'name': 'test station',
        'location': 'test location',
        'working_hours': [{'opening_time': '09:00:00', 'closing_time': '11:00:00', 'weekday': 'friday'}],
        'latitude': -90,
        'longitude': -180,
        'city': 'test city',
    }


@pytest.fixture
async def test_station() -> StationCreatingSchema:
    return StationCreatingSchema(
        **{
            'name': 'test station',
            'location': 'test location',
            'working_hours': [WorkingHoursSchema(opening_time='09:00', closing_time='11:00', weekday=Weekday.FRIDAY)],
            'latitude': -90,
            'longitude': -180,
            'city': 'test city',
        }
    )


@pytest.fixture
async def valid_test_updating_station() -> StationUpdatingSchema:
    return StationUpdatingSchema(
        **{
            'name': 'test updating station',
            'location': 'test updating location',
            'working_hours': [WorkingHoursSchema(opening_time='08:00', closing_time='12:00', weekday=Weekday.MONDAY)],
            'latitude': -90,
            'longitude': -180,
            'city': 'test updating city',
        }
    )


@pytest.fixture
async def invalid_test_updating_station() -> dict:
    return {
        'name': 'test updating station',
        'location': 'test updating location',
        'working_hours': [{'opening_time': '19:00:00', 'closing_time': '11:00:00', 'weekday': 'friday'}],
        'latitude': -90,
        'longitude': -180,
        'city': 'test updating city',
    }
