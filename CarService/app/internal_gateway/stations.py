import json
from uuid import UUID

from fastapi import Depends
from httpx import AsyncClient, AsyncHTTPTransport, HTTPStatusError, RequestError

from app.core.config import get_settings, Settings
from app.core.exceptions import InternalRequestError


class StationGateway:
    PATH_STATIONS = '/stations'
    RETRIES = 3

    def __init__(self, settings: Settings = Depends(get_settings)):
        self.__http_client = AsyncClient(
            transport=AsyncHTTPTransport(retries=self.RETRIES),
            base_url=settings.INTERNAL_STATIONS_URL.rstrip('/'),
        )

    async def get_car_station(self, station_id: UUID) -> dict:
        try:
            response = await self.__http_client.get(
                url=self.PATH_STATIONS,
                params={'station_id': str(station_id)},
            )
            response.raise_for_status()
        except (RequestError, HTTPStatusError, json.JSONDecodeError) as err:
            raise InternalRequestError(status_code=500, message=f'Error internal service request; error: {err}')

        return response.json()
