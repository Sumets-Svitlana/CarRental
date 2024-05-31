from fastapi import Depends
from fastapi_jwt import JwtAuthorizationCredentials

from app.api.config import access_security, get_jwt_subject, refresh_security
from app.api.schemas.auth import AccessToken, RefreshToken
from app.api.schemas.users import UserAuthSchema
from app.api.services.password import hash_password
from app.api.services.users import get_user_service, UserService
from app.core.exceptions import UserGettingError, UserLoginError


class AuthService:
    def __init__(self, user_service: UserService = Depends(get_user_service)):
        self.user_service = user_service

    async def login_user(self, user_auth: UserAuthSchema) -> RefreshToken:
        try:
            user = await self.user_service.get_user_by_email(user_auth.email)
        except UserGettingError as err:
            raise UserLoginError(status_code=err.status_code, message=err.message)

        if user is None or hash_password(user_auth.password) != user.password:
            raise UserLoginError(status_code=401, message='Invalid email or password')
        if user.email_confirmed_at is None:
            raise UserLoginError(status_code=400, message='Email has not been confirmed yet')

        jwt_subject = get_jwt_subject(user.email)
        access_token = access_security.create_access_token(jwt_subject)
        refresh_token = refresh_security.create_refresh_token(jwt_subject)

        return RefreshToken(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def refresh_token(auth: JwtAuthorizationCredentials) -> AccessToken:
        access_token = access_security.create_access_token(subject=auth.subject)
        return AccessToken(access_token=access_token)
