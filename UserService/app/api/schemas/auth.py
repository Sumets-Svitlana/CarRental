from datetime import timedelta

from pydantic import BaseModel

from app.core.config import settings


class AccessToken(BaseModel):
    access_token: str
    access_token_expires: timedelta = settings.ACCESS_EXPIRES


class RefreshToken(AccessToken):
    refresh_token: str
    refresh_token_expires: timedelta = settings.REFRESH_EXPIRES
