from fastapi_jwt import JwtAuthorizationCredentials

from app.api.schemas.users import UserRegistrationSchema, UserSchema
from app.api.services.password import hash_password
from app.core.config import get_settings
from app.core.exceptions import UserCreatingError, UserDeletingError, UserGettingError, UserUpdateError
from app.storage.dynamodb import DynamodbRepository, get_dynamodb


class UserService:
    def __init__(self, table_name: str, email_index: str, dynamodb_client: DynamodbRepository):
        self.dynamodb_client = dynamodb_client
        self.table_name = table_name
        self.email_index = email_index

    async def get_user_by_email(self, email: str) -> UserSchema:
        user = await self.dynamodb_client.query(self.table_name, self.email_index, key_condition={'email': email})
        if not user:
            raise UserGettingError(f'User with email {email} does not exist', 404)

        return UserSchema(**user.pop())

    async def create_user(self, user_auth: UserRegistrationSchema) -> None:
        try:
            await self.get_user_by_email(email=user_auth.email)
        except UserGettingError:
            user_auth.password = hash_password(user_auth.password)
            created = await self.dynamodb_client.put_item(self.table_name, user_auth.model_dump())
            if not created:
                raise UserCreatingError(f'Cannot create user {user_auth.model_dump()}', status_code=409)
            return

        raise UserCreatingError(status_code=409, message='User with that email already exists')

    async def update_user(self, email: str, payload: dict) -> None:
        try:
            user = await self.get_user_by_email(email)
        except UserGettingError as err:
            raise UserUpdateError(err.message, err.status_code)

        updated = await self.dynamodb_client.update_item(self.table_name, {'user_id': user.user_id}, payload=payload)
        if not updated:
            raise UserUpdateError(f'Cannot update user {payload}', status_code=409)

    async def remove_user(self, auth: JwtAuthorizationCredentials) -> None:
        try:
            user = await self.get_user_by_email(auth.subject['username'])
        except UserGettingError as err:
            raise UserDeletingError(status_code=400, message=f'User not found, err: {err.message}')

        deleted = await self.dynamodb_client.delete_item(table_name=self.table_name, key={'user_id': user.user_id})
        if not deleted:
            raise UserDeletingError(f'Cannot delete user {user.email}', status_code=409)


def get_user_service() -> UserService:
    return UserService(
        table_name=get_settings().AWS_DYNAMODB_USER_TABLE_NAME,
        email_index=get_settings().AWS_DYNAMODB_USER_EMAIL_INDEX,
        dynamodb_client=get_dynamodb(),
    )
