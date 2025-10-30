from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional,Literal,List,Dict
class GeneratedVideo(SQLModel):
    __tablename__ ='generated_video'

    id: int | None=Field(default=None,primary_key=True)
    video_session_id: int = Field(foreign_key="video_sessions.id")
    video_url:str = Field(nullable=False)
    resolution:str
    duration_sec:int = Field(nullable=False)
    video_prompt:str = Field(nullable=False)
    images_url:List[Dict[str,str]] = Field(nullable=False)
    status:Literal['PROCESSING','COMPLETED',"FAILED"]
    created_at:datetime = Field(default_factory=datetime.now)
    

