from datetime import datetime
from uuid import UUID

from fastapi import Form
from pydantic import BaseModel, ConfigDict, field_validator, PositiveFloat

from app.core.enums import Brand, CarStatuse, Category, Color, FuelType, Transmission


class BaseCarSchema(BaseModel):
    number: str
    brand: Brand
    year: int
    status: CarStatuse
    description: str | None = None
    transmission: Transmission
    fuel_type: FuelType
    color: Color
    category: Category
    engine_capacity: PositiveFloat
    station_id: UUID
    cost_per_hour: PositiveFloat

    @field_validator('year')
    def over_the_current_year(cls, year: int) -> int:
        current_year = datetime.now().year
        if year < 1900 or year > current_year:
            raise ValueError('Year must be between 1900 and current year')
        return year

    @classmethod
    def as_form(
        cls,
        number: str = Form(),
        brand: Brand = Form(),
        year: int = Form(),
        status: CarStatuse = Form(),
        description: str | None = Form(None),
        transmission: Transmission = Form(),
        fuel_type: FuelType = Form(),
        color: Color = Form(),
        category: Category = Form(),
        engine_capacity: PositiveFloat = Form(),
        station_id: UUID = Form(),
        cost_per_hour: PositiveFloat = Form(),
    ) -> 'BaseCarSchema':
        return cls(
            description=description,
            status=status,
            color=color,
            engine_capacity=engine_capacity,
            fuel_type=fuel_type,
            cost_per_hour=cost_per_hour,
            station_id=station_id,
            transmission=transmission,
            number=number,
            year=year,
            brand=brand,
            category=category,
        )


class CarSchema(BaseCarSchema):
    id: int
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CarCreatingSchema(BaseCarSchema):
    pass


class CarUpdatingSchema(BaseCarSchema):
    pass


class StatusUpdateSchema(BaseModel):
    status: CarStatuse
    car_ids: list[int]
