from httpx import AsyncClient

from app.api.schemas.auth import AccessToken
from app.api.schemas.users import UserSchema
from app.core.config import get_settings
from app.storage.dynamodb import DynamodbRepository
from tests.data import auth_header_token, INVALID_TOKEN, TEST_EMAIL

settings = get_settings()


async def test_current_user_get(client: AsyncClient, auth: AccessToken, confirmed_user: UserSchema):
    headers = auth_header_token(auth.access_token)

    response = await client.get('/user', headers=headers)
    assert response.status_code == 200
    assert response.json() == confirmed_user.model_dump(mode='json')


async def test_unauth_current_user_get(client: AsyncClient):
    headers = auth_header_token(INVALID_TOKEN)
    response = await client.get('/user', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong token: Not enough segments'}


async def test_user_update(client: AsyncClient, auth: AccessToken, repository: DynamodbRepository):
    headers = auth_header_token(auth.access_token)
    payload = {'first_name': 'new_first_name', 'last_name': 'new_last_name'}

    response = await client.put('/user', headers=headers, json=payload)
    assert response.status_code == 204

    users = await repository.query(
        settings.AWS_DYNAMODB_USER_TABLE_NAME,
        settings.AWS_DYNAMODB_USER_EMAIL_INDEX,
        key_condition={'email': TEST_EMAIL},
    )
    user = UserSchema(**users[0])
    assert user.first_name == 'new_first_name'
    assert user.last_name == 'new_last_name'


async def test_unauth_user_update(client: AsyncClient):
    headers = auth_header_token(INVALID_TOKEN)
    payload = {'first_name': 'new_first_name', 'last_name': 'new_last_name'}

    response = await client.put('/user', headers=headers, json=payload)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong token: Not enough segments'}


async def test_user_delete(client: AsyncClient, auth: AccessToken):
    headers = auth_header_token(auth.access_token)

    response = await client.delete('/user', headers=headers)
    assert response.status_code == 204

    response = await client.get('/user', headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        'detail': f'Authorized user cannot be found, err: User with email {TEST_EMAIL} does not exist'
    }


async def test_unauth_user_delete(client: AsyncClient, confirmed_user: UserSchema):
    headers = auth_header_token(INVALID_TOKEN)

    response = await client.delete('/user', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong token: Not enough segments'}
