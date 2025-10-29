from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models.user_model import User
from app.schemas.user import UserSignup, UserLogin, UserRead
from app.db.session import get_session
from typing import List, Optional
from app.utils.security import hash_password, verify_password
#from app.utils.security import create_access_token
#from datetime import timedelta
#from fastapi.responses import JSONResponse
    
#get logged in user

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"]
    )

#REFRESH_TOKEN_EXPIRY=2

@router.post(
        "/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED
        )
def signup(
    user_signup: UserSignup, session: Session = Depends(get_session)
    ):
    
    existing_user = session.exec(select(User).where(User.email == user_signup.email)).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password= hash_password(user_signup.password)

    new_user = User(
        name=user_signup.name,
        email=user_signup.email,
        passwordHash=hashed_password,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {
    "id": new_user.id,
    "name": new_user.name,
    "email": new_user.email,
    "created_at": new_user.created_at,
    "updated_at": new_user.updated_at
}


@router.post(
        "/login", response_model=UserRead
        )
def login(
    user_login: UserLogin, response: Response, session: Session = Depends(get_session)
    ):

    user = session.exec(select(User).where(User.email == user_login.email)).first()

    if not user or not verify_password(user_login.password, user.passwordHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # access_token = create_access_token(
    #     user_data={
    #         "email": user_login.email,
    #     }
    # )

    # refresh_token= create_access_token(
    #     user_data={
    #         "email": user_login.email,
    #     },
    #     refresh=True,
    #     expiry= timedelta(days=REFRESH_TOKEN_EXPIRY)
    # )

    # user.refreshToken = refresh_token
    # session.add(user)  
    # session.commit()
    # session.refresh(user)


    # response.set_cookie(
    #     key="access_token",
    #     value=access_token,
    #     httponly=True,         
    #     max_age=3600,           
    #     secure=True,          
    #     samesite="Strict",
    #     path="/"     
    # )

    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     max_age=REFRESH_TOKEN_EXPIRY * 24 * 3600,  # e.g., 2 days
    #     secure=True,
    #     samesite="Strict",
    #     path= '/auth/refresh'
    # )
    
    # return JSONResponse(
    #     content={
    #         "message": "login successful",
    #         "access_token": access_token,
    #         "refresh_token":refresh_token,
    #         "user":{
    #             "email": user_login.email,
    #         }
    #     },
    # )
    return user
