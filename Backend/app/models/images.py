from sqlmodel import SQLModel,Field
from datetime import datetime
from typing import List,Dict

class Images(SQLModel):
    id:int| None=Field(default=None,primary_key=True)
    model_used:str=Field(nullable=False)
    listOfImages:List[Dict[str,str]]
    approved:bool = Field(default=False)
    created_at:datetime = Field(default_factory=datetime.now)
    story_generate_id:int = Field(foreign_key="story_generate.id")