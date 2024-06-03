from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.api.schemas import CarCreatingSchema, CarSchema
from tests.data import get_test_creating_payload, get_test_updating_payload, TEST_IMAGE
from tests.mocks.s3 import MockS3Manager


async def create_test_car(client: AsyncClient, payload: CarCreatingSchema) -> CarSchema:
    response = await client.post('/cars', data=payload.model_dump(mode='json'), files={'image': TEST_IMAGE})

    assert response.status_code == 200
    return CarSchema(**response.json())


async def test_create_car(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    response = await client.post('/cars', data=payload.model_dump(mode='json'), files={'image': TEST_IMAGE})
    result = CarSchema(**response.json())

    assert response.status_code == 200
    assert result.model_dump(exclude={'id', 'image'}) == payload.model_dump()
    assert result.image == MockS3Manager.THUMBNAIL_URL


async def test_create_car_already_exists(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    await create_test_car(client, payload)

    response = await client.post('/cars', data=payload.model_dump(mode='json'), files={'image': TEST_IMAGE})

    assert response.status_code == 409
    assert response.json()['detail'].startswith(f'Cannot create car with {payload.number}')


async def test_update_car(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    car = await create_test_car(client, payload)

    payload = get_test_updating_payload()
    response = await client.put(f'/cars/{car.id}', data=payload.model_dump(mode='json'), files={'image': TEST_IMAGE})
    result = CarSchema(**response.json())

    assert response.status_code == 200
    assert result.model_dump(exclude={'id', 'image'}) == payload.model_dump()
    assert result.image == MockS3Manager.THUMBNAIL_URL


async def test_update_car_not_found(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_updating_payload()
    response = await client.put('/cars/111', data=payload.model_dump(mode='json'), files={'image': TEST_IMAGE})

    assert response.status_code == 404
    assert response.json() == {'detail': 'Car with id 111 does not exist'}


async def test_list_cars(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    car = await create_test_car(client, payload)

    response = await client.get('/cars')
    result = [CarSchema(**s) for s in response.json()]

    assert response.status_code == 200
    assert result[0].model_dump(exclude={'number', 'id', 'image'}) == car.model_dump(exclude={'number', 'id', 'image'})
    assert result[0].image == MockS3Manager.THUMBNAIL_URL


async def test_getting_car(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    car = await create_test_car(client, payload)

    response = await client.get(f'/cars/{car.id}')
    result = CarSchema(**response.json())

    assert response.status_code == 200
    assert result.model_dump(exclude={'id', 'image'}) == payload.model_dump(exclude={'id', 'image'})
    assert result.image == MockS3Manager.THUMBNAIL_URL


async def test_delete_car(client: AsyncClient, mocker: MockerFixture):
    mocker.patch('app.api.services.StationGateway.get_car_station', return_value=None)

    payload = get_test_creating_payload()
    car = await create_test_car(client, payload)

    response = await client.delete(f'/cars/{car.id}')
    getting_car = await client.get(f'/cars/{car.id}')

    assert response.status_code == 204
    assert getting_car.status_code == 404
    assert getting_car.json() == {'detail': f'Car with id {car.id} does not exist'}


async def test_delete_car_not_found(client: AsyncClient):
    response = await client.delete('/cars/111')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Car with id 111 does not exist'
