from httpx import AsyncClient

from app.api.schemas.users import UserRegistrationSchema, UserSchema
from app.api.services.password import hash_password
from app.core.config import get_settings
from app.storage.dynamodb import DynamodbRepository
from tests.data import TEST_EMAIL, VALID_PASSWORD

settings = get_settings()


async def test_success_user_register(client: AsyncClient, repository: DynamodbRepository):
    payload = UserRegistrationSchema(
        email=TEST_EMAIL,
        first_name='test_first_name',
        last_name='test_last_name',
        password=VALID_PASSWORD,
    )
    response = await client.post('/register', json=payload.model_dump())
    assert response.status_code == 200

    users = await repository.query(
        settings.AWS_DYNAMODB_USER_TABLE_NAME,
        settings.AWS_DYNAMODB_USER_EMAIL_INDEX,
        key_condition={'email': TEST_EMAIL},
    )
    user = UserSchema(**users[0])
    assert user.email == payload.email
    assert user.password == hash_password(payload.password)


async def test_user_already_exist(client: AsyncClient, user: UserSchema, repository: DynamodbRepository):
    payload = UserRegistrationSchema(
        email=TEST_EMAIL,
        first_name='test_first_name',
        last_name='test_last_name',
        password=VALID_PASSWORD,
    )
    response = await client.post('/register', json=payload.model_dump())
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with that email already exists'}


async def test_success_forgot_pass(client: AsyncClient, user: UserSchema):
    response = await client.post('/register/forgot-password', params={'email': TEST_EMAIL})
    assert response.status_code == 200


async def test_forgot_pass_user_not_found(client: AsyncClient):
    response = await client.post('/register/forgot-password', params={'email': TEST_EMAIL})
    assert response.status_code == 404
    assert response.json() == {'detail': f'User with email {TEST_EMAIL} does not exist'}
