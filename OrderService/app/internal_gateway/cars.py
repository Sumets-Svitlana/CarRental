from fastapi import Depends
from httpx import AsyncClient, AsyncHTTPTransport

from app.core.config import get_settings, Settings
from app.core.enums import CarStatuses
from app.internal_gateway.exception_handler import InternalGatewayErrorHandler


class CarGateway:
    PATH_CARS = '/batch-cars'
    PATH_CARS_STATUS = '/update-cars-status'
    RETRIES = 3

    def __init__(self, settings: Settings = Depends(get_settings)):
        self.__http_client = AsyncClient(
            transport=AsyncHTTPTransport(retries=self.RETRIES),
            base_url=settings.INTERNAL_CARS_URL.rstrip('/'),
        )

    @InternalGatewayErrorHandler()
    async def get_cars_by_ids(self, car_ids: list[int]) -> dict:
        response = await self.__http_client.get(
            url=self.PATH_CARS,
            params={'car_ids': car_ids},
        )
        response.raise_for_status()
        return response.json()

    @InternalGatewayErrorHandler()
    async def update_cars_status(self, car_ids: list[int], status: CarStatuses) -> dict:
        response = await self.__http_client.post(
            url=self.PATH_CARS_STATUS,
            json={'car_ids': car_ids, 'status': status},
        )
        response.raise_for_status()
        return response.json()
