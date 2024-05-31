from asyncio import gather

from fastapi import Depends, UploadFile

from app.api.schemas import CarCreatingSchema, CarSchema, CarUpdatingSchema, StatusUpdateSchema
from app.car_app.repository import CarRepository
from app.core.exceptions import (
    CarCreationError,
    CarDeletingError,
    CarGettingError,
    CarUpdateError,
    InternalRequestError,
    UploadFileError,
)
from app.internal_gateway.stations import StationGateway
from app.storage.s3 import get_s3, S3Manager

IMAGE_NAME = '{car_number}_{file_name}'


class CarService:
    def __init__(
        self,
        repository: CarRepository = Depends(),
        s3: S3Manager = Depends(get_s3),
        station_gateway: StationGateway = Depends(),
    ):
        self.repository = repository
        self.s3 = s3
        self.station_gateway = station_gateway

    async def get_cars(self) -> list[CarSchema]:
        cars = await self.repository.get_all()
        cars = await self._set_image_url(cars)
        return cars

    async def get_car(self, car_id: int) -> CarSchema:
        car = await self.repository.get_by_id(car_id)
        car.image = await self.s3.create_presigned_url(car.image)
        return car

    async def create_car(self, creating_schema: CarCreatingSchema, image: UploadFile) -> CarSchema:
        file_name = IMAGE_NAME.format(car_number=creating_schema.number, file_name=image.filename)

        uploaded = await self.s3.upload_file(image, file_name)
        if uploaded is False:
            raise CarCreationError('Cannot update car image', status_code=520)

        try:
            await self.station_gateway.get_car_station(station_id=creating_schema.station_id)
        except InternalRequestError as err:
            raise CarCreationError(f'Cannot find {creating_schema.station_id} station, {err}', status_code=404)

        created_car = await self.repository.create(creating_schema, file_name)
        created_car.image = await self.s3.create_presigned_url(file_name)

        return created_car

    async def update_car(self, car_id: int, updating_schema: CarUpdatingSchema, image: UploadFile) -> CarSchema:
        try:
            file_name = await self._upload_file(car_id, image)
        except UploadFileError as err:
            raise CarUpdateError(err.message, err.status_code)

        try:
            await self.station_gateway.get_car_station(station_id=updating_schema.station_id)
        except InternalRequestError as err:
            raise CarCreationError(f'Cannot find {updating_schema.station_id} station, {err}', status_code=404)

        updated_car = await self.repository.update(car_id, updating_schema, file_name)
        updated_car.image = await self.s3.create_presigned_url(file_name)

        return updated_car

    async def _upload_file(self, car_id: int, image: UploadFile) -> str:
        try:
            old_car = await self.repository.get_by_id(car_id)
        except CarGettingError as err:
            raise UploadFileError(err.message, err.status_code)
        file_name = old_car.image

        if image:
            deleted = await self.s3.delete_objects(file_name)
            if deleted is False:
                raise UploadFileError('Cannot delete car image', status_code=520)

            file_name = IMAGE_NAME.format(car_number=old_car.number, file_name=image.filename)
            uploaded = await self.s3.upload_file(image, file_name)
            if uploaded is False:
                raise UploadFileError('Cannot update car image', status_code=520)

        return file_name

    async def delete_car(self, car_id: int):
        try:
            car = await self.repository.get_by_id(car_id)
        except CarGettingError as err:
            raise CarDeletingError(err.message, err.status_code)

        deleted = await self.s3.delete_objects(car.image)
        if deleted is False:
            raise CarDeletingError('Cannot delete car image', status_code=520)

        await self.repository.remove(car_id)

    async def get_cars_by_ids(self, car_ids: list[int]) -> list[CarSchema]:
        cars = await self.repository.get_by_ids(car_ids)
        cars = await self._set_image_url(cars)
        return cars

    async def update_cars_status(self, status_schema: StatusUpdateSchema) -> list[CarSchema]:
        updated_cars = await self.repository.update_status(status_schema)
        cars = await self._set_image_url(updated_cars)
        return cars

    async def _set_image_url(self, cars: list[CarSchema]) -> list[CarSchema]:
        tasks = [self.s3.create_presigned_url(car.image) for car in cars]
        urls = await gather(*tasks)
        for car, url in zip(cars, urls):
            car.image = url
        return cars
