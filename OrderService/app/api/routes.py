from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.schemas import OrderCreatingSchema, OrderSchema, OrderUpdatingSchema
from app.api.services import OrderService
from app.core.exceptions import OrderCreationError, OrderDeletingError, OrderGettingError, OrderUpdateError
from app.order_app.repository import OrderRepository

router = APIRouter(tags=['Order'])


@router.get('/orders/{order_id}', response_model=OrderSchema)
async def get_order(order_id: PydanticObjectId, repository: OrderRepository = Depends()):
    try:
        order = await repository.get_order_by_id(order_id)
    except OrderGettingError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return order


@router.get('/orders/', response_model=list[OrderSchema])
async def get_all(repository: OrderRepository = Depends()):
    return await repository.get_orders()


@router.post('/orders/', response_model=OrderSchema)
async def create(order_schema: OrderCreatingSchema, order_service: OrderService = Depends()):
    try:
        order = await order_service.add_order(order_schema)
    except OrderCreationError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return order


@router.put('/orders/{order_id}', response_model=OrderSchema)
async def update(
    order_id: PydanticObjectId,
    order_schema: OrderUpdatingSchema,
    order_service: OrderService = Depends(),
):
    try:
        updated_order = await order_service.upgrade_order(order_id, order_schema)
    except OrderUpdateError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))

    return updated_order


@router.delete('/orders/{order_id}', status_code=204, response_class=Response)
async def remove(order_id: PydanticObjectId, order_service: OrderService = Depends()):
    try:
        await order_service.remove_order(order_id)
    except OrderDeletingError as err:
        raise HTTPException(status_code=err.status_code, detail=str(err))
