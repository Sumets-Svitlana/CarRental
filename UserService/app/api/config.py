from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer

from app.core.config import get_settings

access_security = JwtAccessBearer(
    secret_key=get_settings().AUTH_JWT_SECRET_KEY,
    access_expires_delta=get_settings().ACCESS_EXPIRES,
    refresh_expires_delta=get_settings().REFRESH_EXPIRES,
)

refresh_security = JwtRefreshBearer(
    secret_key=get_settings().AUTH_JWT_SECRET_KEY,
    access_expires_delta=get_settings().ACCESS_EXPIRES,
    refresh_expires_delta=get_settings().REFRESH_EXPIRES,
)


def get_jwt_subject(email: str) -> dict[str, str]:
    return {'username': email}
