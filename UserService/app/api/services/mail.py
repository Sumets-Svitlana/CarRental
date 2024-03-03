from datetime import datetime

from fastapi import Depends

from app.api.config import access_security, get_jwt_subject
from app.api.mailer import get_mail_service, MailSender
from app.api.schemas.users import UserSchema
from app.api.services.password import hash_password
from app.api.services.users import get_user_service, UserService
from app.core.exceptions import EmailVerificationError, UserGettingError, UserUpdateError, UserVerificationError

DATATIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class MailService:
    def __init__(
        self,
        user_service: UserService = Depends(get_user_service),
        mail_sender: MailSender = Depends(get_mail_service),
    ):
        self.user_service = user_service
        self.mail_sender = mail_sender

    async def forgot_password(self, email: str) -> None:
        token = await self._get_token(email)
        await self.mail_sender.send_password_reset_email(email, token)

    async def reset_password(self, token: str, password: str) -> None:
        try:
            user = await self._get_user_by_token(token)
            await self.user_service.update_user(email=user.email, payload={'password': hash_password(password)})
        except (UserGettingError, EmailVerificationError, UserUpdateError) as err:
            raise UserVerificationError(status_code=err.status_code, message=err.message)

    async def verify_email(self, email: str) -> None:
        token = await self._get_token(email)
        await self.mail_sender.send_verification_email(email, token)

    async def verify_email_by_token(self, token: str) -> None:
        try:
            user = await self._get_user_by_token(token)
            await self.user_service.update_user(
                email=user.email,
                payload={'email_confirmed_at': datetime.utcnow().strftime(DATATIME_FORMAT)},
            )
        except (UserGettingError, EmailVerificationError, UserUpdateError) as err:
            raise UserVerificationError(status_code=err.status_code, message=err.message)

    async def _get_token(self, email: str) -> str:
        try:
            user = await self.user_service.get_user_by_email(email)
            self._validate_user(user)
        except (UserGettingError, EmailVerificationError) as err:
            raise UserVerificationError(status_code=err.status_code, message=err.message)

        jwt_subject = get_jwt_subject(user.email)
        token = access_security.create_access_token(jwt_subject)
        return token

    async def _get_user_by_token(self, token: str) -> UserSchema:
        payload = access_security._decode(token)
        email = payload['subject']['username']

        user = await self.user_service.get_user_by_email(email)
        self._validate_user(user)

        return user

    @staticmethod
    def _validate_user(user: UserSchema) -> None:
        if user.email_confirmed_at is not None:
            raise EmailVerificationError(status_code=400, message='Email {user.email} has already been confirmed')
