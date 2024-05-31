from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.services.mail import MailService
from app.core.exceptions import UserVerificationError

mail_router = APIRouter(prefix='/mail', tags=['Mail'])


@mail_router.post('/verify', response_class=Response)
async def request_verification_email(email: str, mail_service: MailService = Depends()):
    try:
        await mail_service.verify_email(email)
    except UserVerificationError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=200)


@mail_router.post('/verify/{token}', response_class=Response)
async def verify_email(token: str, mail_service: MailService = Depends()):
    try:
        await mail_service.verify_email_by_token(token)
    except UserVerificationError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    return Response(status_code=200)
