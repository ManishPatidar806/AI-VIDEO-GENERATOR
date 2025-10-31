from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import timedelta, datetime, timezone
from app.core.config import settings
from fastapi import HTTPException, status
import jwt


ph = PasswordHasher()

ACCESS_TOKEN_EXPIRY = 3600

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    

def create_access_token(user_data:dict, expiry: timedelta = None, refresh: bool= False):
    payload = {}

    payload = {
        "user": user_data,
        "type": "refresh" if refresh else "access",  
        "exp": datetime.now(timezone.utc) + (expiry if expiry else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    }

    token= jwt.encode(
        payload= payload,
        key= settings.JWT_SECRET,
        algorithm= settings.JWT_ALGORITHM
    )

    return token


def verify_access_token(token: str, refresh: bool = False) -> dict:
    
    try:

        decoded_token = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        token_type = decoded_token.get("type")

        expected_type = "refresh" if refresh else "access"

        if token_type != expected_type:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {expected_type}, got {token_type}.",
            )

        return decoded_token

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )






