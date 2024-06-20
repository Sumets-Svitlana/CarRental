import json
import uuid

from fakeredis import FakeRedis
from httpx import AsyncClient

from app.api.schemas import StationCreatingSchema, StationUpdatingSchema

TEST_STORAGE = 'stations'


class TestStationsCreate:
    async def test_success(self, client: AsyncClient, redis_client: FakeRedis, valid_test_station_json_data: dict):
        response = await client.post('/stations', content=json.dumps(valid_test_station_json_data))
        valid_test_station_json_data['station_id'] = response.json()['station_id']

        assert response.status_code == 200
        assert response.json() == valid_test_station_json_data

        station = await redis_client.hget(TEST_STORAGE, response.json()['station_id'])
        assert json.loads(station) == valid_test_station_json_data

    async def test_fail_unreal_working_time(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        invalid_test_updating_station: dict,
    ):
        response = await client.post('/stations', content=json.dumps(invalid_test_updating_station))

        assert response.status_code == 422
        assert (
            response.json()['detail'][0]['msg']
            == 'Value error, Closing time (11:00:00) must be greater than opening time (19:00:00)'
        )


class TestStationsUpdate:
    async def test_success(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        test_station: StationCreatingSchema,
        valid_test_updating_station: StationUpdatingSchema,
    ):
        station_id = str(test_station.station_id)
        await redis_client.hset(TEST_STORAGE, station_id, test_station.model_dump_json())

        response = await client.put(
            f'/stations/{station_id}',
            content=valid_test_updating_station.model_dump_json(),
        )
        assert response.status_code == 200

        updating_station = valid_test_updating_station.model_dump(mode='json') | {'station_id': station_id}
        assert response.json() == updating_station

        station = await redis_client.hget(TEST_STORAGE, response.json()['station_id'])
        assert json.loads(station) == updating_station

    async def test_fail_unreal_working_time(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        test_station: StationCreatingSchema,
        invalid_test_updating_station: dict,
    ):
        station_id = str(test_station.station_id)
        await redis_client.hset(TEST_STORAGE, station_id, test_station.model_dump_json())

        response = await client.put(f'/stations/{station_id}', content=json.dumps(invalid_test_updating_station))

        assert response.status_code == 422
        assert (
            response.json()['detail'][0]['msg']
            == 'Value error, Closing time (11:00:00) must be greater than opening time (19:00:00)'
        )

    async def test_fail_station_not_found(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        valid_test_updating_station: StationUpdatingSchema,
    ):
        random_uuid = str(uuid.uuid4())
        response = await client.put(
            f'/stations/{random_uuid}',
            content=valid_test_updating_station.model_dump_json(),
        )

        assert response.status_code == 404
        assert response.json() == {'detail': f'Station {random_uuid} not found'}


class TestStationsList:
    async def test_list_empty(self, client: AsyncClient, redis_client: FakeRedis):
        response = await client.get('/stations')

        assert response.status_code == 200
        assert response.json() == []

    async def test_success_list(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        test_station: StationCreatingSchema,
    ):
        station_id = str(test_station.station_id)
        await redis_client.hset(TEST_STORAGE, station_id, test_station.model_dump_json())

        response = await client.get('/stations')
        assert response.status_code == 200
        assert response.json() == [json.loads(test_station.model_dump_json())]

        station = await redis_client.hget(TEST_STORAGE, station_id)
        assert station == test_station.model_dump_json()


class TestStationsGet:
    async def test_success(self, client: AsyncClient, redis_client: FakeRedis, test_station: StationCreatingSchema):
        station_id = str(test_station.station_id)
        await redis_client.hset(TEST_STORAGE, station_id, test_station.model_dump_json())

        response = await client.get(f'/stations/{station_id}')
        assert response.status_code == 200
        assert response.json() == json.loads(test_station.model_dump_json())

        station = await redis_client.hget(TEST_STORAGE, station_id)
        assert station == test_station.model_dump_json()

    async def test_fail_station_not_found(
        self,
        client: AsyncClient,
        redis_client: FakeRedis,
        test_station: StationCreatingSchema,
    ):
        random_uuid = str(uuid.uuid4())
        response = await client.get(f'/stations/{random_uuid}')
        assert response.status_code == 404
        assert response.json() == {'detail': f'Station {random_uuid} not found'}


class TestStationsDelete:
    async def test_success(self, client: AsyncClient, redis_client: FakeRedis, test_station: StationCreatingSchema):
        station_id = str(test_station.station_id)
        await redis_client.hset(TEST_STORAGE, station_id, test_station.model_dump_json())

        response = await client.delete(f'/stations/{station_id}')
        assert response.status_code == 204

        station = await redis_client.hget(TEST_STORAGE, station_id)
        assert station is None

    async def test_failed_station_not_found(self, client: AsyncClient, redis_client: FakeRedis):
        random_uuid = str(uuid.uuid4())

        response = await client.delete(f'/stations/{random_uuid}')
        assert response.status_code == 404
        assert response.json() == {'detail': f'Station {random_uuid} not found'}

        station = await redis_client.hget(TEST_STORAGE, random_uuid)
        assert station is None
