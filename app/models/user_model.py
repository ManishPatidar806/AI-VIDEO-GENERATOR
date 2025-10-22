from sqlmodel import Field, SQLModel,Relationship
from datetime import datetime
from typing import Optional,List
from app.models.videoSessions_model import VideoSession

class User(SQLModel,table=True):
    __tablename__='users'
    id: int | None=Field(default=None,primary_key=True)
    name:str = Field(max_length=100)
    email:str = Field(index=True,unique=True,max_length=120,nullable=False)
    passwordHash:str = Field(nullable=False)
    refreshToken:Optional[str] = None
    created_at:datetime = Field(default_factory=datetime.utcnow,nullable=False)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})
    video_sessions:List[VideoSession] = Relationship(back_populates="user")
