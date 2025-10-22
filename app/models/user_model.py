from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class User(SQLModel,table=True):
    id: int | None=Field(default=None,primary_key=True)
    name:str = Field(max_length=100)
    email:str = Field(index=True,unique=True,max_length=120)
    passwordHash:str 
    refreshToken:str
    created_at:datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime]=None