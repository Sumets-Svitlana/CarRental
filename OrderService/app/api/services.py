from beanie import PydanticObjectId
from fastapi import Depends

from app.api.schemas import OrderCreatingSchema, OrderUpdatingSchema
from app.core.enums import CarStatuses, OrderStatuses
from app.core.exceptions import (
    InternalRequestError,
    OrderCreationError,
    OrderDeletingError,
    OrderGettingError,
    OrderUpdateError,
)
from app.internal_gateway.cars import CarGateway
from app.models.orders import Order
from app.order_app.repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository = Depends(), car_gateway: CarGateway = Depends()):
        self.car_gateway = car_gateway
        self.repository = repository

    async def add_order(self, order_schema: OrderCreatingSchema) -> Order:
        try:
            cars = await self.car_gateway.get_cars_by_ids(car_ids=order_schema.car_ids)
        except InternalRequestError as err:
            raise OrderCreationError(message=err.message, status_code=err.status_code)

        if not all(car['status'] == CarStatuses.FREE for car in cars):
            raise OrderCreationError(f'Not all cars {order_schema.car_ids} are free', status_code=409)

        try:
            await self.car_gateway.update_cars_status(order_schema.car_ids, CarStatuses.ORDERED)
        except InternalRequestError as err:
            raise OrderCreationError(message=err.message, status_code=err.status_code)

        order = await self.repository.create_order(order_schema)
        return order

    async def upgrade_order(self, order_id: PydanticObjectId, order_schema: OrderUpdatingSchema) -> Order:
        car_status = self._determine_car_status(order_schema.status)

        try:
            await self.car_gateway.update_cars_status(order_schema.car_ids, car_status)
        except InternalRequestError as err:
            raise OrderUpdateError(message=err.message, status_code=err.status_code)

        updated_order = await self.repository.update_order(order_id, order_schema)
        return updated_order

    @staticmethod
    def _determine_car_status(order_status: OrderStatuses) -> CarStatuses:
        if order_status in (OrderStatuses.ORDERED, OrderStatuses.IN_PROGRES):
            return CarStatuses.ORDERED
        if order_status in (OrderStatuses.CANCELED, OrderStatuses.FINISHED):
            return CarStatuses.FREE

    async def remove_order(self, order_id: PydanticObjectId, car_gateway: CarGateway = Depends()):
        try:
            order = await self.repository.get_order_by_id(order_id)
            await car_gateway.update_cars_status(order.car_ids, CarStatuses.FREE)
        except (OrderGettingError, InternalRequestError) as err:
            raise OrderDeletingError(err.message, err.status_code)

        await self.repository.delete_order(order_id)
