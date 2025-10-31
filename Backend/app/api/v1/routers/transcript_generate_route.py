from fastapi import APIRouter, HTTPException
from app.ml.model_connect import (
    transcript_generator,
    story_generator,
    image_generator,
    video_generator,
    generate_voiceover,
    assemble_final_video,
    complete_video_pipeline,

)
from app.schemas.api_response import APIResponse
from app.schemas.ml_process_response import (
    ImageGeneratorResponse,
    VideoGeneratorResponse,
    VideoWithVoiceoverResponse,
)
import logging
from app.schemas.transcript_request import VideoAssembleRequest,VideoClipRequest,VideoRequest,VoiceoverRequest,StoryRequest,ImageRequest,CompletePipelineRequest



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()
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


