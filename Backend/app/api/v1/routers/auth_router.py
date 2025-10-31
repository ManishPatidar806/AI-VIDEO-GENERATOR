from fastapi import APIRouter,Request,Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.user_model import User
from app.schemas.user import UserSignup, UserLogin, UserRead
from app.db.session import get_session
from app.utils.security import hash_password, verify_password
from app.utils.security import create_access_token,verify_access_token
from datetime import timedelta
from fastapi.responses import JSONResponse
    

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"]
    )


REFRESH_TOKEN_EXPIRY=2


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_signup: UserSignup, session: Session = Depends(get_session)):
    
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


@router.post("/login", response_model=UserRead)
def login(user_login: UserLogin, session: Session = Depends(get_session)):

    user = session.exec(select(User).where(User.email == user_login.email)).first()
    
    if not user or not verify_password(user_login.password, user.passwordHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    access_token = create_access_token(
        user_data={
            "email": user_login.email,
        }
    )

    refresh_token= create_access_token(
        user_data={
            "email": user_login.email,
        },
        refresh=True,
        expiry= timedelta(days=REFRESH_TOKEN_EXPIRY)
    )

    response = JSONResponse(
    content={
        "message": "login successful",
        "user": {"email": user_login.email},
    }
    )

    user.refreshToken = refresh_token
    session.add(user)  
    session.commit()
    session.refresh(user)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,         
        max_age=3600,           
        # secure=True, 
        secure=False,        
        # samesite="Strict",
        samesite="Lax",
        path="/"     
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRY * 24 * 3600,  # e.g., 2 days
        # secure=True,
        secure=False,
        # samesite="None",
        samesite="Lax",
        path= '/auth/refresh'
    )
    
    return response


@router.post("/refresh")
def refresh_token(request: Request, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refresh_token")

    print("Cookies received:", request.cookies)

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = verify_access_token(refresh_token, refresh=True)
        email = payload.get("email")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = session.exec(select(User).where(User.email == email)).first()

    if not user or user.refreshToken != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"email": email})

    response = JSONResponse(content={"message": "Access token refreshed"})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        # secure=True,
        secure=False,
        samesite="None",
        max_age=3600,
        path="/",
    )

    return response


@router.post("/logout")
def logout(request: Request, session: Session = Depends(get_session)):

    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:

        user = session.exec(select(User).where(User.refreshToken == refresh_token)).first()

        if user:
            user.refreshToken = None
            session.add(user)
            session.commit()

    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")

    return response


@router.get("/me", response_model=UserRead)
def get_current_user(request: Request, session: Session = Depends(get_session)):
    print("1")
    access_token = request.cookies.get("access_token")
    print("happy")
    print(access_token)
    print("2")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = verify_access_token(access_token)
        email = payload.get("email")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
