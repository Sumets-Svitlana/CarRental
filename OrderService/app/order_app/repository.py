from beanie import PydanticObjectId
from fastapi import Depends
from pymongo.errors import WriteError

from app.api.schemas import BaseOrderSchema, OrderCreatingSchema, OrderUpdatingSchema
from app.core.exceptions import (
    InternalRequestError,
    OrderCreationError,
    OrderDeletingError,
    OrderGettingError,
    OrderUpdateError,
)
from app.internal_gateway.cars import CarGateway
from app.models.orders import Order


class OrderRepository:
    def __init__(self, car_gateway: CarGateway = Depends()):
        self.car_gateway = car_gateway

    @staticmethod
    async def get_order_by_id(order_id: PydanticObjectId) -> Order:
        order = await Order.get(order_id)
        if not order:
            raise OrderGettingError(f'Order with id {order_id} does not exist', 404)
        return order

    @staticmethod
    async def get_orders() -> list[Order]:
        orders = await Order.find_all().to_list()
        return orders

    async def create_order(self, order_schema: OrderCreatingSchema) -> Order:
        total_cost = await self._calculate_total_cost(order_schema)
        full_schema = order_schema.model_dump() | {'total_cost': total_cost}

        try:
            order = await Order(**full_schema).insert()
        except WriteError as err:
            raise OrderCreationError(f'Cannot create order, err={err}', status_code=409)

        return order

    async def update_order(self, order_id: PydanticObjectId, order_schema: OrderUpdatingSchema) -> Order:
        try:
            order = await self.get_order_by_id(order_id)
            total_cost = await self._calculate_total_cost(order_schema)
        except (OrderGettingError, InternalRequestError) as err:
            raise OrderUpdateError(err.message, err.status_code)

        full_schema = order_schema.model_dump() | {'total_cost': total_cost}
        try:
            order = await order.update({'$set': full_schema})
        except WriteError as err:
            raise OrderUpdateError(f'Cannot update order, err={err}', status_code=409)

        return order

    async def delete_order(self, order_id: PydanticObjectId):
        try:
            order = await self.get_order_by_id(order_id)
        except OrderGettingError as err:
            raise OrderDeletingError(err.message, err.status_code)

        await order.delete()

    async def _calculate_total_cost(self, order_schema: BaseOrderSchema) -> float:
        time_difference = order_schema.rental_date_end - order_schema.rental_date_start
        rental_time_hours = int(time_difference.total_seconds() / 3600)

        cars = await self.car_gateway.get_cars_by_ids(car_ids=order_schema.car_ids)
        total_cost = sum(car['cost_per_hour'] * rental_time_hours for car in cars)

        return total_cost
