import re
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, computed_field, constr, EmailStr, field_validator

PASSWORD_RULES = {
    'uppercase letter': r'[A-Z]',
    'lowercase letter': r'[a-z]',
    'digit': r'[0-9]',
    'special character': r'[\W_]',
}


class UserBaseSchema(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str


class UserSchema(UserBaseSchema):
    user_id: str
    password: str
    email_confirmed_at: datetime | None = None


class UserRegistrationSchema(UserBaseSchema):
    password: constr(min_length=8, max_length=128)

    @computed_field
    def user_id(self) -> str:
        return str(uuid4())

    @field_validator('password')
    def validate_password(cls, password: str) -> str:
        for requirement, pattern in PASSWORD_RULES.items():
            if not re.search(pattern, password):
                raise ValueError(f'Password must contain at least one {requirement}')
        return password


class UserUpdateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
