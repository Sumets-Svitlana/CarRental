from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer

from app.core.config import settings

access_security = JwtAccessBearer(
    secret_key=settings.AUTH_JWT_SECRET_KEY,
    access_expires_delta=settings.ACCESS_EXPIRES,
    refresh_expires_delta=settings.REFRESH_EXPIRES,
)

refresh_security = JwtRefreshBearer(
    secret_key=settings.AUTH_JWT_SECRET_KEY,
    access_expires_delta=settings.ACCESS_EXPIRES,
    refresh_expires_delta=settings.REFRESH_EXPIRES,
)


def get_jwt_subject(email: str) -> dict[str, str]:
    return {'username': email}
