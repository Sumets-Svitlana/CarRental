from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import connect_to_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=get_settings().PROJECT_NAME,
        version='0.1.0',
        lifespan=lifespan,
    )
    application.include_router(router)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    return application


app = create_app()
