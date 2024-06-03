from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CarCreatingSchema, CarSchema, CarUpdatingSchema, StatusUpdateSchema
from app.core.database import get_session
from app.core.exceptions import CarCreationError, CarGettingError, CarUpdateError
from app.models.cars import Car


class CarRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session

    async def get_by_id(self, car_id: int) -> CarSchema:
        query = select(Car).where(Car.id == car_id)

        car = await self._session.scalar(query)
        if car is None:
            raise CarGettingError(f'Car with id {car_id} does not exist', 404)

        return CarSchema.model_validate(car)

    async def get_all(self) -> list[CarSchema]:
        query = select(Car)
        cars = await self._session.scalars(query)
        return [CarSchema.model_validate(car) for car in cars]

    async def create(self, car_schema: CarCreatingSchema, file_name: str) -> CarSchema:
        full_schema = car_schema.model_dump() | {'image': file_name}
        query = insert(Car).values(full_schema).returning(Car)

        try:
            car = await self._session.scalar(query)
        except IntegrityError as err:
            raise CarCreationError(f'Cannot create car with {car_schema.number}, err={err}', status_code=409)

        return CarSchema.model_validate(car)

    async def update(self, car_id: int, car_schema: CarUpdatingSchema, file_name: str) -> CarSchema:
        full_schema = car_schema.model_dump() | {'image': file_name}
        query = update(Car).filter(Car.id == car_id).values(full_schema).returning(Car)

        try:
            car = await self._session.scalar(query)
        except IntegrityError as err:
            raise CarUpdateError(f'Cannot update car with {car_schema.model_dump()}, err={err}', status_code=409)

        return CarSchema.model_validate(car)

    async def remove(self, car_id: int):
        query = delete(Car).where(Car.id == car_id)
        await self._session.execute(query)

    async def get_by_ids(self, car_ids: list[int]) -> list[CarSchema]:
        query = select(Car).where(Car.id.in_(car_ids))

        cars = await self._session.scalars(query)
        if cars is None:
            raise CarGettingError(f'Cars with ids {car_ids} do not exist', 404)

        return [CarSchema.model_validate(car) for car in cars]

    async def update_status(self, status_schema: StatusUpdateSchema) -> list[CarSchema]:
        query = update(Car).where(Car.id.in_(status_schema.car_ids)).values(status=status_schema.status).returning(Car)

        try:
            cars = await self._session.scalars(query)
        except IntegrityError as err:
            raise CarUpdateError(f'Cannot update car with {status_schema.model_dump()}, err={err}', status_code=409)

        return [CarSchema.model_validate(car) for car in cars]
