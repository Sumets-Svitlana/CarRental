from httpx import AsyncClient

from app.api.schemas.users import UserSchema
from tests.data import TEST_EMAIL


async def test_success_mail_verify(client: AsyncClient, user: UserSchema):
    response = await client.post('/mail/verify', params={'email': TEST_EMAIL})
    assert response.status_code == 200


async def test_mail_verify_user_not_found(client: AsyncClient):
    response = await client.post('/mail/verify', params={'email': TEST_EMAIL})
    assert response.status_code == 404
    assert response.json() == {'detail': f'User with email {TEST_EMAIL} does not exist'}
