from datetime import datetime, timezone

from pydantic import BaseModel, field_validator, model_validator, PositiveFloat

from app.core.enums import OrderStatuses


class BaseOrderSchema(BaseModel):
    rental_date_start: datetime
    rental_date_end: datetime
    status: OrderStatuses
    customer_id: int
    car_ids: list[int]


class OrderSchema(BaseOrderSchema):
    rental_time: int
    total_cost: PositiveFloat


class BaseOrderValidationSchema(BaseOrderSchema):
    @field_validator('rental_date_start', 'rental_date_end')
    def validate_dates(cls, rental_date: datetime) -> datetime:
        if rental_date < datetime.now(timezone.utc):
            raise ValueError(f'Date {rental_date} cannot be in the past')
        return rental_date

    @model_validator(mode='after')
    def validate_date_ratio(self) -> 'BaseOrderSchema':
        if self.rental_date_end <= self.rental_date_start:
            raise ValueError(
                f'End date ({self.rental_date_end}) must be greater than '
                f'start date ({self.rental_date_start}) for the rental period'
            )
        return self


class OrderCreatingSchema(BaseOrderValidationSchema):
    pass


class OrderUpdatingSchema(BaseOrderValidationSchema):
    pass
