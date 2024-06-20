from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.schemas import StationCreatingSchema, StationSchema, StationUpdatingSchema
from app.api.services import StationService
from app.core.exceptions import AlreadyExistsError, NotFoundError

router = APIRouter(tags=['Station'])


@router.get('/stations')
async def retrieve_stations(station_service: StationService = Depends()) -> list[StationSchema]:
    return await station_service.get_stations()


@router.get('/stations/{station_id}')
async def retrieve_station(station_id: str, station_service: StationService = Depends()) -> StationSchema:
    try:
        station = await station_service.get_station(station_id)
    except NotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return station


@router.post('/stations')
async def create_station(station: StationCreatingSchema, station_service: StationService = Depends()) -> StationSchema:
    try:
        created_station = await station_service.create_station(station)
    except AlreadyExistsError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return created_station


@router.put('/stations/{station_id}')
async def update_station(
    station_id: str,
    station: StationUpdatingSchema,
    station_service: StationService = Depends(),
) -> StationSchema:
    try:
        created_station = await station_service.update_station(station_id, station)
    except NotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return created_station


@router.delete('/stations/{station_id}')
async def delete_station(station_id: str, station_service: StationService = Depends()) -> Response:
    try:
        await station_service.delete_station(station_id)
    except NotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return Response(status_code=204)
