from pydantic import BaseModel, EmailStr, Field, constr
from typing import Annotated, Optional, List
from datetime import datetime


# Shared Base Model (common fields)
class UserBase(BaseModel):
    email: Annotated[
        EmailStr,
        Field(
            max_length=120,
            title="Email Address",
            description="User's unique email address (used for login).",
            example="user@example.com"
        )
    ]


# Signup Model (for registration)
class UserSignup(UserBase):
    name: Annotated[
        str,
        Field(
            min_length=2, 
            max_length=100,
            title="Full Name",
            description="Full name of the user (2–100 characters).",
            example="Ravi Kumar"
        )
    ]



    password: Annotated[
        str,
        Field(
            min_length=8,
            title="Password",
            description="Strong password (8–128 characters).",
            example="MySecurePass123!"
        )
    ]



# Login Model (for authentication)
class UserLogin(UserBase):
    # email: Annotated[
    #     EmailStr,
    #     Field(
    #         max_length=120,
    #         title="Email Address",
    #         description="Registered email used for login.",
    #         example="user@example.com"
    #     )
    # ]

    password: Annotated[
        str,
        Field(
            min_length=8,
            title="Password",
            description="User's account password.",
            example="MySecurePass123!"
        )
    ]


# Read Model (returned after login/signup)
class UserRead(UserBase):
    id: Annotated[
        int,
        Field(
            default=None,
            title="User ID",
            description="Unique identifier for the user.",
            example=1
        )
    ]= None

    name: Annotated[
        str,
        Field(
            title="Full Name",
            description="Name of the user.",
            example="Sonal Gupta"
        )
    ]

    created_at: Annotated[
        datetime,
        Field(
            title="Account Created At",
            description="Timestamp when the user account was created (UTC).",
            example="2025-10-28T12:45:00Z"
        )
    ]

    updated_at: Annotated[
        Optional[datetime],
        Field(
            default=None,
            title="Last Updated",
            description="Timestamp when the user details were last updated (UTC).",
            example="2025-10-29T09:15:00Z"
        )
    ]= None

    class Config:
        from_attributes = True


# Optional: Token Response Model (after login/signup)
class TokenResponse(BaseModel):
    # access_token: Annotated[
    #     str,
    #     Field(
    #         title="Access Token",
    #         description="JWT access token for authenticated requests.",
    #         example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    #     )
    # ]

    refresh_token: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Refresh Token",
            description="Token used to refresh authentication when access token expires.",
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )
    ]= None



# Extended Model with Related Data
# -----------------------------------------
class UserWithSessions(UserRead):
    video_sessions: Annotated[
        List["VideoSessionRead"],  
        Field(
            default=[],
            title="Video Sessions",
            description="List of video sessions associated with this user."
        )
    ] = []
