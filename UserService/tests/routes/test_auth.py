from httpx import AsyncClient

from app.api.schemas.auth import AccessToken, RefreshToken
from app.api.schemas.users import UserSchema
from tests.data import auth_header_token, INVALID_PASSWORD, INVALID_TOKEN, TEST_INVALID_EMAIL, VALID_PASSWORD


async def test_not_authorized(client: AsyncClient) -> None:
    resp = await client.get('/user')
    assert resp.status_code == 401
    headers = auth_header_token(INVALID_TOKEN)
    resp = await client.get('/user', headers=headers)
    assert resp.status_code == 401


async def test_email_not_confirmed_yet(client: AsyncClient, user: UserSchema):
    response = await client.post('/auth/login', json={'email': user.email, 'password': VALID_PASSWORD})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Email has not been confirmed yet'}


async def test_invalid_email(client: AsyncClient, user: UserSchema):
    response = await client.post('/auth/login', json={'email': TEST_INVALID_EMAIL, 'password': VALID_PASSWORD})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User with email invalid_email@gmail.com does not exist'}


async def test_invalid_password(client: AsyncClient, user: UserSchema):
    response = await client.post('/auth/login', json={'email': user.email, 'password': INVALID_PASSWORD})
    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid email or password'}


async def test_success_login(client: AsyncClient, dynamodb, confirmed_user: UserSchema):
    response = await client.post('/auth/login', json={'email': confirmed_user.email, 'password': VALID_PASSWORD})
    assert response.status_code == 200
    token = AccessToken(**response.json())

    headers = auth_header_token(token.access_token)
    response = await client.get('/user', headers=headers)
    assert response.status_code == 200
    assert response.json() == confirmed_user.model_dump(mode='json')


async def test_success_refresh_token(client: AsyncClient, confirmed_user: UserSchema):
    response = await client.post('/auth/login', json={'email': confirmed_user.email, 'password': VALID_PASSWORD})
    assert response.status_code == 200
    token = RefreshToken(**response.json())

    headers = auth_header_token(token.refresh_token)
    response = await client.post('/auth/refresh', headers=headers)
    assert response.status_code == 200
    AccessToken(**response.json())

    headers = auth_header_token(token.access_token)
    response = await client.get('/user', headers=headers)
    assert response.status_code == 200
    assert response.json() == confirmed_user.model_dump(mode='json')


async def test_invalid_refresh_token(client: AsyncClient, confirmed_user: UserSchema):
    headers = auth_header_token(INVALID_TOKEN)
    response = await client.post('/auth/refresh', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong token: Not enough segments'}
