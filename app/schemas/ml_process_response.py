from pydantic import BaseModel,Field
from typing import List,Optional

class StoryGeneratorResponse(BaseModel):
    scene: str = Field(..., description="The title of the scene")
    narration: str = Field(..., description="The creative narration or dialogue for this scene")
    visual_cues: str = Field(..., description="Detailed description of visuals, characters, environment, and mood")
    prompts: List[str] = Field(..., description="List of AI image generation prompts for this scene")

class StoryListResponse(BaseModel):
    scenes: List[StoryGeneratorResponse]


class ImageGeneratorResponse(BaseModel):
    scene: str = Field(..., description="The title of the scene")
    narration: str = Field(..., description="The creative narration or dialogue for this scene")
    visual_cues: str = Field(..., description="Detailed description of visuals, characters, environment, and mood")
    prompts: List[str] = Field(..., description="List of AI image generation prompts for this scene")
    image_path: Optional[str] = Field(default=None, description="Local path or details of the generated image")

class VideoGeneratorResponse(BaseModel):
    scene: str = Field(..., description="The title of the scene")
    narration: str = Field(..., description="The creative narration or dialogue for this scene")
    visual_cues: str = Field(..., description="Detailed description of visuals, characters, environment, and mood")
    prompts: List[str] = Field(..., description="List of AI image generation prompts for this scene")
    image: Optional[str] = Field(default=None, description="Path to the reference image used for generation")
    video_path: Optional[str] = Field(default=None, description="Local path of the generated video clip")


class VideoWithVoiceoverResponse(BaseModel):
    scene: str = Field(..., description="The title of the scene")
    narration: str = Field(..., description="The creative narration or dialogue for this scene")
    visual_cues: str = Field(..., description="Detailed description of visuals, characters, environment, and mood")
    prompts: List[str] = Field(..., description="List of AI image generation prompts for this scene")
    image: Optional[str] = Field(default=None, description="Local path or details of the generated image")
    video_path: Optional[str] = Field(default=None, description="Local path of the generated video clip")
    voiceover: Optional[str] = Field(default=None, description="Local path to the voiceover audio file")

