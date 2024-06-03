import secrets
import string
from io import BytesIO

from app.api.schemas import CarCreatingSchema, CarUpdatingSchema
from app.core.enums import Brand, CarStatuse, Category, Color, FuelType, Transmission

TEST_IMAGE = BytesIO(b'some test image')


def generate_random_string(length: int) -> str:
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_test_creating_payload() -> CarCreatingSchema:
    number = generate_random_string(10)
    return CarCreatingSchema(
        number=number,
        brand=Brand.HONDA,
        year=2001,
        status=CarStatuse.FREE,
        description='Some test description',
        transmission=Transmission.HYDROSTATIC,
        fuel_type=FuelType.HYBRID,
        color=Color.GRAY,
        category=Category.COMPACT,
        engine_capacity=123.6,
        station_id='47e19740-6d65-418c-8752-e5c3753848d8',
        cost_per_hour=12.6,
    )


def get_test_updating_payload() -> CarUpdatingSchema:
    number = generate_random_string(10)
    return CarUpdatingSchema(
        number=number,
        brand=Brand.HONDA,
        year=2001,
        status=CarStatuse.FREE,
        description='Some test description',
        transmission=Transmission.HYDROSTATIC,
        fuel_type=FuelType.HYBRID,
        color=Color.GRAY,
        category=Category.COMPACT,
        engine_capacity=123.6,
        station_id='47e19740-6d65-418c-8752-e5c3753848d8',
        cost_per_hour=12.6,
    )
