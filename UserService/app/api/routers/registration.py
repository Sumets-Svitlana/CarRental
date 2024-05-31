from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.schemas.users import UserRegistrationSchema
from app.api.services.mail import MailService
from app.api.services.users import get_user_service, UserService
from app.core.exceptions import UserCreatingError, UserVerificationError

register_router = APIRouter(prefix='/register', tags=['Register'])


@register_router.post('', response_class=Response)
async def register_user(user_auth: UserRegistrationSchema, user_service: UserService = Depends(get_user_service)):
    try:
        await user_service.create_user(user_auth)
    except UserCreatingError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=200)


@register_router.post('/forgot-password', response_class=Response)
async def forgot_password(email: str, mail_service: MailService = Depends()) -> Response:
    try:
        await mail_service.forgot_password(email)
    except UserVerificationError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=200)


@register_router.post('/reset-password/{token}', response_class=Response)
async def reset_password(token: str, password: str, mail_service: MailService = Depends()):
    try:
        await mail_service.reset_password(token, password)
    except UserVerificationError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=200)
