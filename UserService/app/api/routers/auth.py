from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials

from app.api.config import refresh_security
from app.api.schemas.auth import AccessToken, RefreshToken
from app.api.schemas.users import UserAuthSchema
from app.api.services.auth import AuthService
from app.core.exceptions import UserLoginError

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/login', response_model=RefreshToken)
async def login(user_auth: UserAuthSchema, auth_service: AuthService = Depends()):
    try:
        tokens = await auth_service.login_user(user_auth)
    except UserLoginError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return tokens


@auth_router.post('/refresh', response_model=AccessToken)
async def refresh(
    auth: JwtAuthorizationCredentials = Security(refresh_security),
    auth_service: AuthService = Depends(),
):
    return await auth_service.refresh_token(auth)
