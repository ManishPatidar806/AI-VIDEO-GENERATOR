from sqlmodel import SQLModel, Field
from datetime import datetime

class Summaries(SQLModel,table=True):
    __tablename__="summaries"
    id:int| None=Field(default=None,primary_key=True)
    summary_text:str=Field(nullable=False)
    model_used:str=Field(nullable=False)
    created_at:datetime = Field(default_factory=datetime.now)
    video_session_id:int = Field(foreign_key="video_sessions.id")
    