from sqlmodel import SQLModel,Field
from datetime import datetime
from typing import List

# !Currently we are store only user data and not any other type of Data. In future if required we can store
class StoryGenerate(SQLModel):
    __tablename__="story_generate"
    id:int| None=Field(default=None,primary_key=True)
    story_text:str = Field(nullable=False)
    approved:bool = Field(default=False)
    model_user:str = Field(nullable=False)
    imagePrompts:List[str] 
    created_at:datetime = Field(default_factory=datetime.now)
    summary_id:int = Field(foreign_key="summaries.id")