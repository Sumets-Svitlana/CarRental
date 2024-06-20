from functools import lru_cache
from urllib.parse import urljoin

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.api.email_texts import (
    EMAIL_VERIFICATION_BODY,
    EMAIL_VERIFICATION_SUBJECT,
    PASSWORD_RESET_BODY,
    PASSWORD_RESET_SUBJECT,
)
from app.core.config import get_settings


class MailSender:
    MAIL_VERIFICATION_PATH = '/mail/verify/'
    RESET_PASSWORD_PATH = '/register/reset-password/'

    def __init__(self, mail: FastMail):
        self.__mail = mail
        self.base_url = get_settings().INTERNAL_USER_URL

    async def send_verification_email(self, email: str, token: str):
        url = urljoin(self.base_url, f'{self.MAIL_VERIFICATION_PATH}{token}')

        message = MessageSchema(
            recipients=[email],
            subject=EMAIL_VERIFICATION_SUBJECT,
            body=EMAIL_VERIFICATION_BODY.format(url=url),
            subtype=MessageType.plain,
        )

        await self.__mail.send_message(message)

    async def send_password_reset_email(self, email: str, token: str):
        url = urljoin(self.base_url, f'{self.RESET_PASSWORD_PATH}{token}')

        message = MessageSchema(
            recipients=[email],
            subject=PASSWORD_RESET_SUBJECT,
            body=PASSWORD_RESET_BODY.format(url=url),
            subtype=MessageType.plain,
        )

        await self.__mail.send_message(message)


@lru_cache
def get_mail_service() -> MailSender:
    mail = FastMail(
        ConnectionConfig(
            MAIL_USERNAME=get_settings().MAIL_USERNAME,
            MAIL_PASSWORD=get_settings().MAIL_PASSWORD,
            MAIL_FROM=get_settings().MAIL_SENDER,
            MAIL_PORT=get_settings().MAIL_PORT,
            MAIL_SERVER=get_settings().MAIL_SERVER,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
        )
    )
    return MailSender(mail=mail)
