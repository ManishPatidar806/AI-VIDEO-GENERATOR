from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models.user_model import User
from app.schemas.user import UserSignup, UserLogin, UserRead
from app.db.session import get_session
from typing import List, Optional
from app.utils.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from pydantic import BaseModel

class AuthResponse(BaseModel):
    token: str
    user: UserRead

router = APIRouter()

REFRESH_TOKEN_EXPIRY = 7  # days

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(user_signup: UserSignup, session: Session = Depends(get_session)):
    
    existing_user = session.exec(select(User).where(User.email == user_signup.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user_signup.password)

    new_user = User(
        name=user_signup.name,
        email=user_signup.email,
        passwordHash=hashed_password,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        user_data={
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
    )
    
    user_data = UserRead(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )
    
    return AuthResponse(token=access_token, user=user_data)


@router.post("/login", response_model=AuthResponse)
def login(
    user_login: UserLogin, response: Response, session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == user_login.email)).first()

    if not user or not verify_password(user_login.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        user_data={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )
    
    user_data = UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return AuthResponse(token=access_token, user=user_data)
