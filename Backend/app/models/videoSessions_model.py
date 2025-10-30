from sqlmodel import SQLModel ,Field,Relationship
from datetime import datetime
from typing import Optional,Literal
from app.models.user_model import User

class VideoSessions(SQLModel,table=True):
    __tablename__ ='video_sessions'

    id: int | None=Field(default=None,primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    
    youtube_url:str = Field(nullable=False)
    title:str
    transcript_text:str = Field(nullable=False)
    status:Literal["PENDING",'PROCESSING','COMPLETED',"FAILED"]
    created_at:datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime]=None





    user: Optional[User]=Relationship(back_populates='video_sessions')