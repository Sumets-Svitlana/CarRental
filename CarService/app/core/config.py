from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = 'CarService'

    DATABASE_URL: PostgresDsn

    AWS_S3_CARS_BUCKET_NAME: str
    AWS_S3_ENDPOINT_URL: str | None = None

    INTERNAL_STATIONS_URL: str

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file='.env',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
