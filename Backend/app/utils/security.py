from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import timedelta, datetime, timezone
from app.core.config import settings
import jwt
import os


ph = PasswordHasher()

ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY = 7 * 24 * 3600  # 7 days

# Use environment variable or fallback to a default for development
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production-12345678")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload['refresh'] = refresh
    payload['iat'] = datetime.now(timezone.utc)

    token = jwt.encode(
        payload=payload,
        key=JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return token_data
    
    except jwt.PyJWTError as e:
        return None



