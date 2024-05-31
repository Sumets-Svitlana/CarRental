import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode(), settings.AUTH_JWT_SALT.encode())
    hashed_password = hashed_bytes.decode()
    return hashed_password
