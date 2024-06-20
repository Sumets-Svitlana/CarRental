import os
from asyncio import DefaultEventLoopPolicy, gather
from contextlib import asynccontextmanager

import boto3
import pytest
import yaml
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from moto import mock_aws

from app.api.schemas.tables import UserTableSchema
from app.api.schemas.users import UserRegistrationSchema, UserSchema
from app.api.services.password import hash_password
from app.core.config import get_settings
from app.storage.async_runner import run_async
from app.storage.dynamodb import DynamodbRepository
from tests.data import TEST_EMAIL, VALID_PASSWORD

TEST_HOST = 'http://test'
TABLES_PATH = 'tests/models.yaml'


def pytest_configure(config: pytest.Config):
    os.environ['AWS_DYNAMODB_ENDPOINT_URL'] = ''
    os.environ['AWS_DYNAMODB_USER_TABLE_NAME'] = 'Test-User'
    os.environ['AWS_DYNAMODB_USER_EMAIL_INDEX'] = 'email-index'


@pytest.fixture(scope='session', params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param


@pytest.fixture(scope='session')
async def app() -> FastAPI:
    from app.main import create_app

    _app = create_app()

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client


@asynccontextmanager
async def async_mock_aws():
    with mock_aws():
        yield


@pytest.fixture(scope='function', autouse=True)
async def dynamodb():
    async with async_mock_aws():
        await downgrade()
        await upgrade()
        yield


@run_async
def downgrade():
    dynamodb_resource = boto3.resource('dynamodb')
    for table in dynamodb_resource.tables.all():
        table.delete()


async def upgrade():
    with open(TABLES_PATH) as file:
        tables = yaml.safe_load(file)

    repository = DynamodbRepository(endpoint_url=None)
    tasks = (repository.create_tables(name, UserTableSchema(**schema)) for name, schema in tables.items())
    await gather(*tasks)


@pytest.fixture
def registration_data() -> UserRegistrationSchema:
    return UserRegistrationSchema(
        email=TEST_EMAIL,
        first_name='test_first_name',
        last_name='test_last_name',
        password=hash_password(VALID_PASSWORD),
    )


@pytest.fixture
def repository() -> DynamodbRepository:
    return DynamodbRepository(endpoint_url=None)


@pytest.fixture
async def auth(client: AsyncClient, confirmed_user: UserSchema):
    from app.api.config import access_security, get_jwt_subject
    from app.api.schemas.auth import AccessToken

    jwt_subject = get_jwt_subject(TEST_EMAIL)
    access_token = access_security.create_access_token(jwt_subject)
    token = AccessToken(access_token=access_token)
    return token


@pytest.fixture
async def user(repository: DynamodbRepository, registration_data: UserRegistrationSchema) -> UserSchema:
    settings = get_settings()

    await repository.put_item(settings.AWS_DYNAMODB_USER_TABLE_NAME, registration_data.model_dump())
    users = await repository.query(
        settings.AWS_DYNAMODB_USER_TABLE_NAME,
        settings.AWS_DYNAMODB_USER_EMAIL_INDEX,
        key_condition={'email': TEST_EMAIL},
    )
    return UserSchema(**users[0])


@pytest.fixture
async def confirmed_user(repository: DynamodbRepository, user: UserSchema) -> UserSchema:
    settings = get_settings()

    payload = {'email_confirmed_at': '2024-06-07 16:19:19.798967'}
    key = {'user_id': user.user_id}

    await repository.update_item(settings.AWS_DYNAMODB_USER_TABLE_NAME, key, payload=payload)
    users = await repository.query(
        settings.AWS_DYNAMODB_USER_TABLE_NAME,
        settings.AWS_DYNAMODB_USER_EMAIL_INDEX,
        key_condition={'email': TEST_EMAIL},
    )
    user = UserSchema(**users[0])
    return user
