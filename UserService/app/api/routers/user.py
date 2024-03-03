from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials

from app.api.config import access_security
from app.api.schemas.users import UserSchema, UserUpdateSchema
from app.api.services.current_user import get_current_user
from app.api.services.users import get_user_service, UserService
from app.core.exceptions import UserDeletingError, UserUpdateError

user_router = APIRouter(prefix='/user', tags=['User'])


@user_router.get('', response_model=UserSchema)
async def get_user(user: UserSchema = Depends(get_current_user)):
    return user


@user_router.put('', response_class=Response)
async def update_user(
    update_schema: UserUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.update_user(email=current_user.email, payload=update_schema.model_dump())
    except UserUpdateError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=204)


@user_router.delete('')
async def delete_user(
    auth: JwtAuthorizationCredentials = Security(access_security),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.remove_user(auth)
    except UserDeletingError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=204)
