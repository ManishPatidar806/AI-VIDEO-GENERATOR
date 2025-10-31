from fastapi import HTTPException,APIRouter
import logging as logger
from app.ml.model_connect import (
    regenerate_story_with_modifications,
    regenerate_specific_scenes,
    regenerate_single_image,
    regenerate_single_video,
    regenerate_single_voiceover,
    modify_scene_with_user_input,
    modify_image_prompt_and_generate
)
from app.schemas.api_response import APIResponse, ErrorResponse
from app.schemas.ml_process_response import (
    StoryListResponse,
    ImageGeneratorResponse,
    VideoGeneratorResponse,
    VideoWithVoiceoverResponse,
    StoryGeneratorResponse
)
from app.schemas.transcript_request import RegenerateSpecificScenesRequest,RegenerateStoryRequest,RegenerateSingleImageRequest,RegenerateSingleVideoRequest,RegenerateSingleVoiceoverRequest,UpdateSceneRequest,ImageRequest,VideoClipRequest
router = APIRouter()
# ===== REGENERATION ENDPOINTS =====

@router.post("/story", response_model=APIResponse)
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


@router.post("/specific-scenes", response_model=APIResponse)
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


@router.post("/image", response_model=APIResponse)
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


@router.post("/video", response_model=APIResponse)
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


@router.post("/voiceover", response_model=APIResponse)
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


@router.post("/modify-scene", response_model=APIResponse)
def modify_scene(request: dict):
    """
    Modify a scene based on user input/feedback.
    AI will merge the current scene data with user's requested changes.
    
    Expected request body:
    {
        "scene_data": { ... current scene data ... },
        "user_input": "user's requested changes",
        "summary": "optional video summary for context"
    }
    """
    try:
        logger.info("Modifying scene based on user input")
        
        scene_data = request.get("scene_data")
        user_input = request.get("user_input", "")
        summary = request.get("summary", "")
        
        if not scene_data or not user_input:
            raise HTTPException(
                status_code=400,
                detail="scene_data and user_input are required"
            )
        
        scene = StoryGeneratorResponse(**scene_data)
        
        modified_scene = modify_scene_with_user_input(
            scene=scene,
            user_input=user_input,
            summary=summary
        )
        
        if modified_scene is None:
            raise HTTPException(
                status_code=500,
                detail="Scene modification failed"
            )
        
        logger.info(f"Scene modified successfully: {modified_scene.scene}")
        return APIResponse(
            success=True,
            message="Scene modified successfully based on user input",
            data=modified_scene.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error modifying scene: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify scene: {str(e)}"
        )


@router.post("/modify-image", response_model=APIResponse)
def modify_image(request: dict):
    """
    Modify image prompt based on user input and generate new image.
    AI will merge the current prompt with user's requested changes.
    
    Expected request body:
    {
        "scene_data": { ... current scene data with image prompt ... },
        "user_input": "user's requested changes for the image",
        "output_dir": "optional output directory"
    }
    """
    try:
        logger.info("Modifying image based on user input")
        
        scene_data = request.get("scene_data")
        user_input = request.get("user_input", "")
        output_dir = request.get("output_dir", "nebius_scene_images")
        
        if not scene_data or not user_input:
            raise HTTPException(
                status_code=400,
                detail="scene_data and user_input are required"
            )
        
        scene = StoryGeneratorResponse(**scene_data)
        
        new_image = modify_image_prompt_and_generate(
            scene=scene,
            user_input=user_input,
            output_dir=output_dir
        )
        
        if new_image is None:
            raise HTTPException(
                status_code=500,
                detail="Image modification and generation failed"
            )
        
        logger.info(f"Image modified and generated successfully: {new_image.image}")
        return APIResponse(
            success=True,
            message="Image modified and generated successfully based on user input",
            data=new_image.model_dump(),
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error modifying image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify image: {str(e)}"
        )

