from datetime import timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = 'UserService'

    ACCESS_EXPIRES: timedelta = timedelta(minutes=15)
    REFRESH_EXPIRES: timedelta = timedelta(days=30)

    AWS_DYNAMODB_ENDPOINT_URL: str | None = None
    AWS_DYNAMODB_USER_TABLE_NAME: str
    AWS_DYNAMODB_USER_EMAIL_INDEX: str

    AUTH_JWT_SECRET_KEY: str
    AUTH_JWT_SALT: str

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SENDER: str

    INTERNAL_USER_URL: str

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file='.env',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
