from datetime import time
from functools import cached_property
from uuid import UUID, uuid4

from pydantic import BaseModel, computed_field, ConfigDict, model_validator
from pydantic_extra_types.coordinate import Latitude, Longitude

from app.core.enums import Weekday


class WorkingHoursSchema(BaseModel):
    opening_time: time
    closing_time: time
    weekday: Weekday

    @model_validator(mode='after')
    def validate_working_time(self):
        if self.closing_time <= self.opening_time:
            raise ValueError(
                f'Closing time ({self.closing_time}) must be greater than opening time ({self.opening_time})'
            )
        return self


class StationBaseSchema(BaseModel):
    name: str
    location: str
    working_hours: list[WorkingHoursSchema]
    latitude: Latitude
    longitude: Longitude
    city: str


class StationSchema(StationBaseSchema):
    station_id: UUID

    model_config = ConfigDict(from_attributes=True)


class StationCreatingSchema(StationBaseSchema):
    @computed_field
    @cached_property
    def station_id(self) -> UUID:
        return uuid4()


class StationUpdatingSchema(StationBaseSchema):
    pass
