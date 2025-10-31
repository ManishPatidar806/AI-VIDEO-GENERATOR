from pydantic import BaseModel, Field
from typing import Optional, List

# ===== Request Models =====
class VideoRequest(BaseModel):
    videoId: str = Field(..., description="YouTube video ID")


class StoryRequest(BaseModel):
    summary: str = Field(..., description="Video summary text")


class ImageRequest(BaseModel):
    story_data: List[dict] = Field(..., description="List of story scenes")
    output_dir: Optional[str] = Field(default="generated_images", description="Output directory for images")


class VideoClipRequest(BaseModel):
    image_data: List[dict] = Field(..., description="List of image scenes with paths")
    output_dir: Optional[str] = Field(default="generated_videos", description="Output directory for videos")


class VoiceoverRequest(BaseModel):
    video_data: List[dict] = Field(..., description="List of video scenes with paths")
    output_dir: Optional[str] = Field(default="voice_overs", description="Output directory for voiceovers")


class VideoAssembleRequest(BaseModel):
    scenes_with_voiceovers: List[dict] = Field(..., description="List of scenes with video and voiceover paths")
    bg_music_path: Optional[str] = Field(default=None, description="Path to background music file")
    output_file: Optional[str] = Field(default="final_ai_video.mp4", description="Output filename")


class CompletePipelineRequest(BaseModel):
    videoId: str = Field(..., description="YouTube video ID")
    output_video_name: Optional[str] = Field(default="final_ai_video.mp4", description="Output video filename")


# ===== REGENERATION Request Models =====
class RegenerateStoryRequest(BaseModel):
    summary: str = Field(..., description="Original video summary")
    modifications: Optional[str] = Field(default=None, description="User instructions for modifications (e.g., 'Make it more dramatic', 'Add more technical details')")
    existing_story: Optional[dict] = Field(default=None, description="Existing story data to improve upon")


class RegenerateSpecificScenesRequest(BaseModel):
    scene_indices: List[int] = Field(..., description="List of scene indices to regenerate (0-based)")
    existing_story: dict = Field(..., description="Current complete story data")
    summary: str = Field(..., description="Original video summary")


class RegenerateSingleImageRequest(BaseModel):
    scene_data: dict = Field(..., description="Scene data with prompts")
    output_dir: Optional[str] = Field(default="generated_images", description="Output directory")


class RegenerateSingleVideoRequest(BaseModel):
    image_scene_data: dict = Field(..., description="Scene data with image path")
    output_dir: Optional[str] = Field(default="generated_videos", description="Output directory")


class RegenerateSingleVoiceoverRequest(BaseModel):
    scene_data: dict = Field(..., description="Scene data with narration")
    output_dir: Optional[str] = Field(default="voice_overs", description="Output directory")


class UpdateSceneRequest(BaseModel):
    story_data: dict = Field(..., description="Complete story data")
    scene_index: int = Field(..., description="Index of scene to update (0-based)")
    updated_scene: dict = Field(..., description="Updated scene data")
