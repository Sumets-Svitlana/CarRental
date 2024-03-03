from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials

from app.api.config import access_security
from app.api.schemas.users import UserSchema
from app.api.services.users import get_user_service, UserService
from app.core.exceptions import UserGettingError


async def get_current_user(
    auth: JwtAuthorizationCredentials = Security(access_security),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    if not auth:
        raise HTTPException(status_code=401, detail='No authorization credentials found')

    try:
        user = await user_service.get_user_by_email(auth.subject['username'])
    except UserGettingError as err:
        raise HTTPException(status_code=err.status_code, detail=f'Authorized user cannot be found, err: {err.message}')

    return user
