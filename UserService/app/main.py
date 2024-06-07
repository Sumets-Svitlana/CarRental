from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routers.auth import auth_router
from app.api.routers.mail import mail_router
from app.api.routers.registration import register_router
from app.api.routers.user import user_router
from app.core.config import get_settings
from app.core.database import migrate_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await migrate_db()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=get_settings().PROJECT_NAME,
        version='0.1.0',
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    application.include_router(register_router)
    application.include_router(mail_router)
    application.include_router(auth_router)
    application.include_router(user_router)

    return application


app = create_app()
