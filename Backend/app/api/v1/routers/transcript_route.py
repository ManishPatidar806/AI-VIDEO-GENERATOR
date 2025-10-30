from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional, List
from app.ml.model_connect import (
    transcript_generator,
    story_generator,
    image_generator,
    video_generator,
    generate_voiceover,
    assemble_final_video,
    complete_video_pipeline,
    # Regeneration functions
    regenerate_story_with_modifications,
    regenerate_specific_scenes,
    regenerate_single_image,
    regenerate_single_video,
    regenerate_single_voiceover
)
from app.schemas.api_response import APIResponse, ErrorResponse
from app.schemas.ml_process_response import (
    StoryListResponse,
    ImageGeneratorResponse,
    VideoGeneratorResponse,
    VideoWithVoiceoverResponse,
    StoryGeneratorResponse
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


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


# ===== Endpoints =====

@router.post("/transcript", response_model=APIResponse)
def generate_transcript(request: VideoRequest):
    """
    Generate summary/transcript from YouTube video
    """
    try:
        logger.info(f"Generating transcript for video ID: {request.videoId}")
        summary = transcript_generator(request.videoId)
        
        # Check if error response
        if isinstance(summary, dict) and not summary.get("success", True):
            return APIResponse(
                success=False,
                message=summary.get("message", "Failed to generate transcript"),
                data=None,
                status_code=summary.get("status", 404)
            )
        
        logger.info("Transcript generated successfully")
        return APIResponse(
            success=True,
            message="Transcript generated successfully",
            data={"summary": summary},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating transcript: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate transcript: {str(e)}"
        )


@router.post("/story", response_model=APIResponse)
def generate_story(request: StoryRequest):
    """
    Generate story/script from summary
    """
    try:
        logger.info("Generating story from summary")
        story = story_generator(request.summary)
        
        if story is None:
            raise HTTPException(
                status_code=500,
                detail="Story generation failed"
            )
        
        logger.info(f"Story generated with {len(story.scenes)} scenes")
        return APIResponse(
            success=True,
            message=f"Story generated successfully with {len(story.scenes)} scenes",
            data=story.model_dump(),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story: {str(e)}"
        )


@router.post("/images", response_model=APIResponse)
def generate_images(request: ImageRequest):
    """
    Generate images from story scenes
    """
    try:
        logger.info(f"Generating images for {len(request.story_data)} scenes")
        
        # Convert dict to StoryGeneratorResponse objects
        from app.schemas.ml_process_response import StoryGeneratorResponse
        scenes = [StoryGeneratorResponse(**scene) for scene in request.story_data]
        
        images = image_generator(scenes, output_dir=request.output_dir)
        
        logger.info(f"Generated {len(images)} images successfully")
        return APIResponse(
            success=True,
            message=f"Generated {len(images)} images successfully",
            data={"images": [img.model_dump() for img in images]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate images: {str(e)}"
        )


@router.post("/videos", response_model=APIResponse)
def generate_videos(request: VideoClipRequest):
    """
    Generate video clips from image scenes
    """
    try:
        logger.info(f"Generating videos for {len(request.image_data)} scenes")
        
        # Convert dict to ImageGeneratorResponse objects
        images = [ImageGeneratorResponse(**img) for img in request.image_data]
        
        videos = video_generator(images, output_dir=request.output_dir)
        
        logger.info(f"Generated {len(videos)} videos successfully")
        return APIResponse(
            success=True,
            message=f"Generated {len(videos)} videos successfully",
            data={"videos": [vid.model_dump() for vid in videos]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate videos: {str(e)}"
        )


@router.post("/voiceovers", response_model=APIResponse)
def generate_voiceovers(request: VoiceoverRequest):
    """
    Generate voiceovers for video scenes
    """
    try:
        logger.info(f"Generating voiceovers for {len(request.video_data)} scenes")
        
        # Convert dict to VideoGeneratorResponse objects
        videos = [VideoGeneratorResponse(**vid) for vid in request.video_data]
        
        voices = generate_voiceover(videos, output_dir=request.output_dir)
        
        logger.info(f"Generated {len(voices)} voiceovers successfully")
        return APIResponse(
            success=True,
            message=f"Generated {len(voices)} voiceovers successfully",
            data={"voiceovers": [v.model_dump() for v in voices]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating voiceovers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate voiceovers: {str(e)}"
        )


@router.post("/final-video", response_model=APIResponse)
def generate_final_video(request: VideoAssembleRequest):
    """
    Assemble final video from scenes with voiceovers
    """
    try:
        logger.info(f"Assembling final video with {len(request.scenes_with_voiceovers)} scenes")
        
        # Convert dict to VideoWithVoiceoverResponse objects
        scenes = [VideoWithVoiceoverResponse(**scene) for scene in request.scenes_with_voiceovers]
        
        output = assemble_final_video(
            scenes_with_voiceovers=scenes,
            output_file=request.output_file,
            bg_music_path=request.bg_music_path
        )
        
        if output is None:
            raise HTTPException(
                status_code=500,
                detail="Final video assembly failed"
            )
        
        logger.info(f"Final video created: {output}")
        return APIResponse(
            success=True,
            message="Final video created successfully",
            data={"final_video": output},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error assembling final video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assemble final video: {str(e)}"
        )


@router.post("/complete-pipeline", response_model=APIResponse)
def run_complete_pipeline(request: CompletePipelineRequest):
    """
    Run the complete video generation pipeline from YouTube video ID to final video
    """
    try:
        logger.info(f"Starting complete pipeline for video ID: {request.videoId}")
        
        # Step 1: Generate transcript
        logger.info("Step 1: Generating transcript...")
        summary = transcript_generator(request.videoId)
        
        if isinstance(summary, dict) and not summary.get("success", True):
            raise HTTPException(
                status_code=404,
                detail=summary.get("message", "Failed to generate transcript")
            )
        
        # Step 2: Generate story
        logger.info("Step 2: Generating story...")
        story = story_generator(summary)
        
        if story is None:
            raise HTTPException(
                status_code=500,
                detail="Story generation failed"
            )
        
        # Step 3: Run complete pipeline
        logger.info("Step 3: Running complete video pipeline...")
        final_video = complete_video_pipeline(
            story_scenes=story.scenes,
            output_video_name=request.output_video_name
        )
        
        if final_video is None:
            raise HTTPException(
                status_code=500,
                detail="Complete pipeline failed"
            )
        
        logger.info(f"Complete pipeline finished: {final_video}")
        return APIResponse(
            success=True,
            message="Complete video pipeline executed successfully",
            data={
                "summary": summary,
                "scenes_count": len(story.scenes),
                "final_video": final_video
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in complete pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Complete pipeline failed: {str(e)}"
        )


# ===== REGENERATION ENDPOINTS =====

@router.post("/regenerate/story", response_model=APIResponse)
def regenerate_story(request: RegenerateStoryRequest):
    """
    Regenerate or modify the story with user instructions.
    Use this when user wants to change tone, style, or add specific elements.
    
    Example modifications:
    - "Make it more dramatic and suspenseful"
    - "Add more technical details"
    - "Make it suitable for children"
    - "Focus more on the emotional aspects"
    """
    try:
        logger.info("Regenerating story with modifications")
        
        existing_story_obj = None
        if request.existing_story:
            existing_story_obj = StoryListResponse(**request.existing_story)
        
        regenerated_story = regenerate_story_with_modifications(
            summary=request.summary,
            modifications=request.modifications,
            existing_story=existing_story_obj
        )
        
        if regenerated_story is None:
            raise HTTPException(
                status_code=500,
                detail="Story regeneration failed"
            )
        
        logger.info(f"Story regenerated with {len(regenerated_story.scenes)} scenes")
        return APIResponse(
            success=True,
            message=f"Story regenerated successfully with {len(regenerated_story.scenes)} scenes",
            data=regenerated_story.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating story: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate story: {str(e)}"
        )


@router.post("/regenerate/specific-scenes", response_model=APIResponse)
def regenerate_scenes(request: RegenerateSpecificScenesRequest):
    """
    Regenerate specific scenes by their indices while keeping others intact.
    Useful when user wants to improve only certain scenes.
    
    Example: scene_indices=[0, 3, 5] will regenerate scenes 0, 3, and 5
    """
    try:
        logger.info(f"Regenerating scenes: {request.scene_indices}")
        
        existing_story = StoryListResponse(**request.existing_story)
        
        updated_story = regenerate_specific_scenes(
            scenes_to_regenerate=request.scene_indices,
            existing_story=existing_story,
            summary=request.summary
        )
        
        if updated_story is None:
            raise HTTPException(
                status_code=500,
                detail="Scene regeneration failed"
            )
        
        logger.info(f"Successfully regenerated {len(request.scene_indices)} scenes")
        return APIResponse(
            success=True,
            message=f"Regenerated {len(request.scene_indices)} scenes successfully",
            data=updated_story.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating specific scenes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate scenes: {str(e)}"
        )


@router.post("/regenerate/image", response_model=APIResponse)
def regenerate_image(request: RegenerateSingleImageRequest):
    """
    Regenerate a single image for a specific scene.
    Use when user is not satisfied with a particular image.
    """
    try:
        logger.info(f"Regenerating image for scene")
        
        scene = StoryGeneratorResponse(**request.scene_data)
        
        new_image = regenerate_single_image(
            scene=scene,
            output_dir=request.output_dir
        )
        
        if new_image is None:
            raise HTTPException(
                status_code=500,
                detail="Image regeneration failed"
            )
        
        logger.info(f"Image regenerated: {new_image.image}")
        return APIResponse(
            success=True,
            message="Image regenerated successfully",
            data=new_image.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate image: {str(e)}"
        )


@router.post("/regenerate/video", response_model=APIResponse)
def regenerate_video(request: RegenerateSingleVideoRequest):
    """
    Regenerate a single video clip for a specific scene.
    Use when user wants a different video variation.
    """
    try:
        logger.info(f"Regenerating video clip for scene")
        
        image_scene = ImageGeneratorResponse(**request.image_scene_data)
        
        new_video = regenerate_single_video(
            image_scene=image_scene,
            output_dir=request.output_dir
        )
        
        if new_video is None:
            raise HTTPException(
                status_code=500,
                detail="Video regeneration failed"
            )
        
        logger.info(f"Video regenerated: {new_video.video_path}")
        return APIResponse(
            success=True,
            message="Video regenerated successfully",
            data=new_video.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate video: {str(e)}"
        )


@router.post("/regenerate/voiceover", response_model=APIResponse)
def regenerate_voiceover(request: RegenerateSingleVoiceoverRequest):
    """
    Regenerate a single voiceover for a specific scene.
    Note: Currently uses gTTS, so output will be similar. 
    Future: Can add different voice options or TTS services.
    """
    try:
        logger.info(f"Regenerating voiceover for scene")
        
        scene = VideoGeneratorResponse(**request.scene_data)
        
        new_voiceover = regenerate_single_voiceover(
            scene=scene,
            output_dir=request.output_dir
        )
        
        if new_voiceover is None:
            raise HTTPException(
                status_code=500,
                detail="Voiceover regeneration failed"
            )
        
        logger.info(f"Voiceover regenerated: {new_voiceover.voiceover}")
        return APIResponse(
            success=True,
            message="Voiceover regenerated successfully",
            data=new_voiceover.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating voiceover: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate voiceover: {str(e)}"
        )


@router.put("/update/scene", response_model=APIResponse)
def update_scene(request: UpdateSceneRequest):
    """
    Update a specific scene with new data provided by user.
    Use when user wants to manually edit a scene's narration, visual cues, or prompts.
    """
    try:
        logger.info(f"Updating scene at index {request.scene_index}")
        
        story = StoryListResponse(**request.story_data)
        
        if request.scene_index < 0 or request.scene_index >= len(story.scenes):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scene index. Must be between 0 and {len(story.scenes) - 1}"
            )
        
        # Update the scene
        updated_scene = StoryGeneratorResponse(**request.updated_scene)
        story.scenes[request.scene_index] = updated_scene
        
        logger.info(f"Scene {request.scene_index} updated successfully")
        return APIResponse(
            success=True,
            message=f"Scene {request.scene_index} updated successfully",
            data=story.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scene: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update scene: {str(e)}"
        )


@router.post("/batch-regenerate/images", response_model=APIResponse)
def batch_regenerate_images(request: ImageRequest):
    """
    Regenerate multiple images at once.
    Useful when user wants to regenerate all images or multiple images.
    """
    try:
        logger.info(f"Batch regenerating images for {len(request.story_data)} scenes")
        
        scenes = [StoryGeneratorResponse(**scene) for scene in request.story_data]
        
        new_images = []
        for i, scene in enumerate(scenes):
            logger.info(f"Regenerating image {i+1}/{len(scenes)}")
            new_image = regenerate_single_image(scene, output_dir=request.output_dir)
            if new_image:
                new_images.append(new_image)
        
        logger.info(f"Batch regenerated {len(new_images)} images")
        return APIResponse(
            success=True,
            message=f"Successfully regenerated {len(new_images)} images",
            data={"images": [img.model_dump() for img in new_images]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error in batch image regeneration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch image regeneration failed: {str(e)}"
        )


@router.post("/batch-regenerate/videos", response_model=APIResponse)
def batch_regenerate_videos(request: VideoClipRequest):
    """
    Regenerate multiple video clips at once.
    """
    try:
        logger.info(f"Batch regenerating videos for {len(request.image_data)} scenes")
        
        images = [ImageGeneratorResponse(**img) for img in request.image_data]
        
        new_videos = []
        for i, image_scene in enumerate(images):
            logger.info(f"Regenerating video {i+1}/{len(images)}")
            new_video = regenerate_single_video(image_scene, output_dir=request.output_dir)
            if new_video:
                new_videos.append(new_video)
        
        logger.info(f"Batch regenerated {len(new_videos)} videos")
        return APIResponse(
            success=True,
            message=f"Successfully regenerated {len(new_videos)} videos",
            data={"videos": [vid.model_dump() for vid in new_videos]},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error in batch video regeneration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch video regeneration failed: {str(e)}"
        )

