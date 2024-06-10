TEST_EMAIL = 'test_email@gmail.com'
TEST_INVALID_EMAIL = 'invalid_email@gmail.com'
VALID_PASSWORD = 'Test_Password_11'
INVALID_PASSWORD = 'InvalidPass'
INVALID_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbG'


def auth_header_token(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}
