import bcrypt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode(), get_settings().AUTH_JWT_SALT.encode())
    hashed_password = hashed_bytes.decode()
    return hashed_password
