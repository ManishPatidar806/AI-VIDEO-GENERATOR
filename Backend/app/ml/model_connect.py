from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from moviepy import concatenate_videoclips,CompositeAudioClip,AudioFileClip,VideoFileClip
from langchain_google_genai import ChatGoogleGenerativeAI 
from app.core.config import settings
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from openai import OpenAI
import requests
import os
from gtts import gTTS
import time
from google import genai
from google.genai import types
videoId = "9ofL45Mrzj0"
import uuid 
from app.schemas.ml_process_response import ImageGeneratorResponse,StoryGeneratorResponse,VideoWithVoiceoverResponse,VideoGeneratorResponse,StoryListResponse
from app.utils.prompt_template import image_generator_prompt , summary_prompt
from app.schemas.api_response import TranscriptUploadResponse



OUTPUT_DIR = "nebius_scene_images"
# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',google_api_key=settings.GOOGLE_API_KEY)
client = genai.Client()

pydanticParser = PydanticOutputParser(pydantic_object=StoryListResponse)

# ! Youtube Transcript and Summary Generator
def transcript_generator(videoId:str)->str:
    try:
        summary=""
        api = YouTubeTranscriptApi()
        transcriptList = api.fetch(video_id=videoId, languages=['en'])
        transcript = " ".join(chunk.text for chunk in transcriptList.snippets)
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        chunks = splitter.split_text(transcript)
        for doc in chunks:
            prompt = summary_prompt(doc,summary)
            summary = llm.invoke(prompt)
        return summary.content
    except TranscriptsDisabled:
         return TranscriptUploadResponse(message="NO CONTENT FOUND OR NO TRANSCRIPT FOUND",status=404,success=False)
    except Exception:
         return TranscriptUploadResponse(message="Video is Not Available",status=404,success=False)   
        


# ! Video Script Generator
def story_generator(summary:str):
    try:
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',google_api_key=settings.GOOGLE_API_KEY , temperature=1.2) 
        prompt = image_generator_prompt(summary,pydanticParser)
        print("Prompt Generated")
        formatted_prompt = prompt.format(
        video_summary=summary,
        )
        result = llm.invoke(formatted_prompt)
        parsed_output = pydanticParser.parse(result.content)
        return parsed_output
    except Exception as e:
        print(e)
        print("Somthing went worng in story generator script")    



# ! Image  Generator
def image_generator(scenes: List["StoryGeneratorResponse"], output_dir: str) -> List["ImageGeneratorResponse"]:
    """
    Generates images via the Nebius AI API, saves them locally, 
    and returns a list of ImageGeneratorResponse objects with the local path.
    """
    generated_scenes_with_images = []

    # ✅ Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=settings.NEBIUS_API_KEYS
        )
    except NameError:
        print("ERROR: 'settings' or 'settings.NEBIUS_API_KEYS' is not defined.")
        return []

    asset_counter = 1

    for scene_data in scenes:
        # ✅ Skip scenes with no valid prompts
        if not scene_data.prompts or not scene_data.prompts[0]:
            print(f"Skipping scene '{scene_data.scene}': No valid prompt provided.")
            continue

        prompt_text = scene_data.prompts[0]
        scene_title_safe = scene_data.scene.replace(' ', '_').replace(':', '')

        # ✅ Avoid Pydantic ValidationError: add image=None
        scene_dict = scene_data.model_dump()
        scene_dict["image"] = None
        scene_with_image = ImageGeneratorResponse(**scene_dict)

        print(f"[{asset_counter}/{len(scenes)}] Generating image for: {scene_data.scene}...")

        try:
            # 1️⃣ Generate Image from Nebius AI API
            response = client.images.generate(
                model="black-forest-labs/flux-dev",
                prompt=prompt_text,
            )

            # 2️⃣ Extract the Image URL safely
            image_url = getattr(response.data[0], "url", None)
            if not image_url:
                raise ValueError("No image URL returned by Nebius API.")

            print(f"  -> API call successful. Downloading image...")

            # 3️⃣ Download and store image locally
            image_filename = os.path.join(output_dir, f"{asset_counter}_{scene_title_safe}.png")
            image_response = requests.get(image_url, stream=True)
            image_response.raise_for_status()

            with open(image_filename, 'wb') as file:
                for chunk in image_response.iter_content(chunk_size=8192):
                    file.write(chunk)

            # 4️⃣ Update model with local path
            scene_with_image.image = image_filename
            print(f"  -> Image saved: {image_filename}")

        except Exception as e:
            print(f"  -> ERROR generating/saving image for '{scene_data.scene}': {e}")

        generated_scenes_with_images.append(scene_with_image)
        asset_counter += 1

    print("\n✅ Image generation phase complete.")
    return generated_scenes_with_images


# !Video Generator
def video_generator(images: List["ImageGeneratorResponse"], output_dir: str = "generated_videos") -> List["VideoGeneratorResponse"]:
    """
    Generates short video clips for each scene using the Veo 3.1 model.
    Optionally uses a local image reference (from image generation).

    Args:
        images: List of ImageGeneratorResponse objects containing prompts and image paths.
        output_dir: Directory where generated video clips will be saved.

    Returns:
        A list of VideoGeneratorResponse objects with video paths populated.
    """
    os.makedirs(output_dir, exist_ok=True)
    videos = []

    for i, image in enumerate(images, 1):
        uploaded_file = None
        safe_title = image.scene.replace(" ", "_").replace(":", "")
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(output_dir, f"{i}_{safe_title}_{unique_id}.mp4")

        # Prepare VideoGeneratorResponse base object
        video_scene = VideoGeneratorResponse(
            scene=image.scene,
            narration=image.narration,
            visual_cues=image.visual_cues,
            prompts=image.prompts,
            image=image.image,
            video_path=None,
        )

        try:
            # --- 1️⃣ Upload reference image if available ---
            if image.image and os.path.exists(image.image):
                print(f"\n📤 Uploading reference image: {image.image}")
                uploaded_file = client.files.upload(file=image.image)
                print(f"✅ Uploaded reference: {uploaded_file.name}")

            # --- 2️⃣ Configure generation parameters ---
            config_kwargs = {
                "duration_seconds": 4,  # typical short cinematic
                "aspect_ratio": "16:9",
            }
            if uploaded_file:
                config_kwargs["reference_images"] = [uploaded_file]
            config = types.GenerateVideosConfig(**config_kwargs)

            # --- 3️⃣ Generate video ---
            print(f"🎬 Generating video for scene: {image.scene}")
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=image.visual_cues,
                config=config,
            )

            # --- 4️⃣ Poll until video generation completes ---
            print("⏳ Waiting for video generation (may take a few minutes)...")
            while not operation.done:
                print(".", end="", flush=True)
                time.sleep(10)
                operation = client.operations.get(operation.name)

            # --- 5️⃣ Download the generated video ---
            if getattr(operation, "response", None) and getattr(operation.response, "generated_videos", None):
                generated_video = operation.response.generated_videos[0]
                client.files.download(file=generated_video.video, output_path=output_path)
                video_scene.video_path = output_path
                print(f"\n✅ Video generated and saved: {output_path}")
            else:
                print(f"\n❌ Video generation failed for scene: {image.scene}")
                print(f"Error details: {getattr(operation, 'error', 'No details available')}")

        except Exception as e:
            print(f"\n🔥 Error generating video for {image.scene}: {e}")

        finally:
            # --- 6️⃣ Clean up uploaded file ---
            if uploaded_file:
                try:
                    client.files.delete(name=uploaded_file.name)
                    print(f"🧹 Deleted temporary upload: {uploaded_file.name}")
                except Exception as cleanup_err:
                    print(f"⚠️ Cleanup failed: {cleanup_err}")

        videos.append(video_scene)

    print("\n🎥 All videos processed successfully.")
    return videos


# ! Generate Voice
def generate_voiceover(scenes_with_images: List["VideoGeneratorResponse"], output_dir="voice_overs") -> List["VideoWithVoiceoverResponse"]:
    """
    Generates free voiceover using Google Text-to-Speech (gTTS) for all scenes.
    Returns list of scenes with voiceover paths added.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    scenes_with_voiceovers = []
    
    print("\n🎤 Starting Voiceover Generation Phase ---")
    
    for i, scene in enumerate(scenes_with_images):
        tts_path = os.path.join(output_dir, f"{scene.scene.replace(' ', '_').replace(':', '')}.mp3")
        
        # Create new response object with voiceover field
        scene_dict = scene.model_dump()
        scene_dict["voiceover"] = None
        scene_with_voiceover = VideoWithVoiceoverResponse(**scene_dict)
        
        try:
            print(f"[{i+1}/{len(scenes_with_images)}] Generating voiceover for scene: {scene.scene}")
            tts = gTTS(text=scene.narration, lang='en', slow=False)
            tts.save(tts_path)
            scene_with_voiceover.voiceover = tts_path
            print(f"  -> Voiceover saved: {tts_path}")
        except Exception as e:
            print(f"  -> ⚠️ Failed to generate voiceover for {scene.scene}: {e}")
        
        scenes_with_voiceovers.append(scene_with_voiceover)
    
    print("✅ Voiceover generation phase complete.\n")
    return scenes_with_voiceovers



WORDS_PER_SECOND = 2.5 
def assemble_final_video(scenes_with_voiceovers: List[VideoWithVoiceoverResponse], output_file="final_ai_video.mp4", bg_music_path=None):
    """
    Assemble final video automatically:
    - Uses AI-generated video clips
    - Synchronizes TTS voiceovers
    - Adds background music (optional)
    
    Takes list of scenes with video clips and voiceovers already generated.
    """
    final_clips = []
    audio_segments = []
    total_time = 0

    print("\n🎬 Starting Final Video Assembly (Video Clips + Narration) ---")

    for i, scene_data in enumerate(scenes_with_voiceovers):
        video_path = scene_data.video_path
        if not video_path or not os.path.exists(video_path):
            # Check for video_path, not image_path
            print(f"⚠️ Skipping Scene {i+1}: Missing video clip -> {video_path}")
            continue

        voiceover_path = scene_data.voiceover
        if not voiceover_path or not os.path.exists(voiceover_path):
            print(f"⚠️ Skipping Scene {i+1}: No voiceover for scene '{scene_data.scene}'")
            continue

        # Load narration audio to get duration
        narration_audio = AudioFileClip(voiceover_path)
        duration = narration_audio.duration

        # --- FIX 1: Use VideoFileClip to load the generated video clip ---
        print(f"[{i+1}/{len(scenes_with_voiceovers)}] Adding scene: {scene_data.scene} (duration: {duration:.2f}s)")
        video_clip = VideoFileClip(video_path)
        
        # --- Logic: Set video clip duration to match the narration duration ---
        # If the narration is longer than the clip (e.g., 4s clip, 7s audio), loop the clip or extend the duration.
        # Simple solution: Set the video clip duration to the audio duration.
        # If the video is shorter, moviepy automatically extends the clip by looping the frames or showing the last frame.
        video_clip = video_clip.with_duration(duration)
        video_clip = video_clip.set_audio(narration_audio) # Set the primary audio track

        final_clips.append(video_clip)

        # Add narration timing
        # We add the audio clip (which is now the primary audio for the video_clip)
        audio_segments.append(narration_audio.with_start(total_time))
        total_time += duration

    if not final_clips:
        print("❌ No valid video clips found. Exiting.")
        return None

    print(f"\n📹 Concatenating {len(final_clips)} video clips...")
    # Concatenate video clips
    final_video_clip = concatenate_videoclips(final_clips, method="compose")

    # Merge voiceovers + background music
    print("🎵 Compositing audio tracks...")
    
    # We now only need to composite the background music, as narration is on the video clips
    if bg_music_path and os.path.exists(bg_music_path):
        print(f"  -> Adding background music: {bg_music_path}")
        bg_music = AudioFileClip(bg_music_path).with_volume_scaled(0.25).subclip(0, final_video_clip.duration)
        # Use CompositeAudioClip to mix the main video audio (narration) with background music
        # The narration audio from the video clips is accessed via final_video_clip.audio
        final_audio = CompositeAudioClip([final_video_clip.audio, bg_music])
        final_video_clip = final_video_clip.set_audio(final_audio)
    
    # If no background music, the narration (set via video_clip.set_audio) remains the audio.

    # Export final video
    print(f"\n🎥 Exporting final video to {output_file} ...")
    final_video_clip.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Final video created successfully: {output_file}")
    print(f"   Total duration: {final_video_clip.duration:.2f} seconds")

    return output_file


# ===== COMPLETE PIPELINE FUNCTION =====
def complete_video_pipeline(story_scenes: List["StoryGeneratorResponse"], output_video_name="final_ai_video.mp4"):
    """
    Complete pipeline: 
    Story Scripts → Reference Images (Nebius) → Video Clips (Veo) → Voiceovers → Final Video Assembly

    Args:
        story_scenes: List of StoryGeneratorResponse objects from story_generator()
        output_video_name: Name of the final output video file

    Returns:
        Path to the final assembled video
    """
    print("=" * 60)
    print("🚀 STARTING COMPLETE VIDEO GENERATION PIPELINE (Veo Enabled)")
    print("=" * 60)

    # --- Step 1: Generate Reference Images (Nebius/Flux) ---
    # These images are used as visual cues or references for the Veo model.
    print("\n📸 STEP 1: Generating reference images for all scenes (using Nebius/Flux)...")
    scenes_with_images = image_generator(scenes=story_scenes, output_dir=OUTPUT_DIR)

    if not scenes_with_images:
        print("❌ No images generated. Aborting pipeline.")
        return None

    # --- Step 2: Generate Video Clips (Veo 3.1) ---
    # The Veo function uses the prompts/images from the previous step to create video clips.
    # We must define a new directory for the videos to avoid mixing with reference images.
    VIDEO_CLIPS_DIR = "generated_videos" 
    os.makedirs(VIDEO_CLIPS_DIR, exist_ok=True)
    print(f"\n🎥 STEP 2: Generating video clips for all scenes (using Veo 3.1 in {VIDEO_CLIPS_DIR})...")
    scenes_with_videos = video_generator(
        images=scenes_with_images, 
        output_dir=VIDEO_CLIPS_DIR
    )

    if not scenes_with_videos:
        print("❌ No video clips generated. Aborting pipeline.")
        return None

    # --- Step 3: Generate Voiceovers (gTTS) ---
    # The voiceover function now takes the list of scenes WITH video paths.
    print("\n🎤 STEP 3: Generating voiceovers for all scenes...")
    # NOTE: generate_voiceover now expects VideoGeneratorResponse objects (which contain video_path)
    scenes_with_voiceovers = generate_voiceover(scenes_with_images=scenes_with_videos)

    if not scenes_with_voiceovers:
        print("❌ No voiceovers generated. Aborting pipeline.")
        return None

    # --- Step 4: Assemble Final Video (MoviePy) ---
    print("\n🎬 STEP 4: Assembling final video from video clips and voiceovers...")

    final_video_path = assemble_final_video(
        scenes_with_voiceovers=scenes_with_voiceovers,
        output_file=output_video_name
    )

    print("\n" + "=" * 60)
    if final_video_path:
        print("PIPELINE COMPLETE!")
        print(f"Final video: {final_video_path}")
    else:
        print("Pipeline failed to create video.")
    print("=" * 60)

    return final_video_path


# ===== REGENERATION FUNCTIONS =====

def regenerate_story_with_modifications(summary: str, modifications: str = None, existing_story: StoryListResponse = None):
    """
    Regenerate story with user modifications or instructions.
    
    Args:
        summary: Original video summary
        modifications: User instructions for modifications (e.g., "Make it more dramatic", "Add more technical details")
        existing_story: Optional existing story to modify
    
    Returns:
        StoryListResponse with modified scenes
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash',
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=1.2
        )
        
        # Build the prompt with modifications
        base_prompt = image_generator_prompt(summary)
        
        if modifications:
            modification_instruction = f"\n\nIMPORTANT MODIFICATIONS REQUESTED BY USER:\n{modifications}\n\nPlease incorporate these modifications while maintaining the overall structure and format."
            formatted_prompt = base_prompt.format(video_summary=summary) + modification_instruction
        elif existing_story:
            # If regenerating from existing, provide context
            existing_scenes = "\n".join([f"- {scene.scene}: {scene.narration[:100]}..." for scene in existing_story.scenes])
            formatted_prompt = base_prompt.format(video_summary=summary) + f"\n\nExisting scenes for reference:\n{existing_scenes}\n\nPlease create a fresh version with improvements."
        else:
            formatted_prompt = base_prompt.format(video_summary=summary)
        
        result = llm.invoke(formatted_prompt)
        parsed_output = pydanticParser.parse(result.content)
        return parsed_output
    except Exception as e:
        print(f"Error regenerating story: {e}")
        return None


def regenerate_specific_scenes(scenes_to_regenerate: List[int], existing_story: StoryListResponse, summary: str):
    """
    Regenerate specific scenes by index while keeping others intact.
    
    Args:
        scenes_to_regenerate: List of scene indices to regenerate (0-based)
        existing_story: Current story with all scenes
        summary: Original video summary
    
    Returns:
        StoryListResponse with specified scenes regenerated
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash',
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=1.3  # Slightly higher for variation
        )
        
        new_scenes = list(existing_story.scenes)  # Copy existing scenes
        
        for idx in scenes_to_regenerate:
            if 0 <= idx < len(new_scenes):
                old_scene = new_scenes[idx]
                
                # Create a prompt to regenerate this specific scene
                regenerate_prompt = f"""
Based on the video summary below, regenerate the scene titled "{old_scene.scene}".

Video Summary:
{summary}

Current scene that needs improvement:
- Scene: {old_scene.scene}
- Narration: {old_scene.narration}
- Visual Cues: {old_scene.visual_cues}

Please provide a FRESH and IMPROVED version of this scene with:
1. A compelling narration
2. Detailed visual cues
3. AI-ready image generation prompts

Return ONLY a valid JSON object with this structure:
{{
    "scene": "Scene title",
    "narration": "Detailed narration text",
    "visual_cues": "Detailed visual description",
    "prompts": ["Image generation prompt"]
}}
"""
                
                result = llm.invoke(regenerate_prompt)
                # Parse the result as a single scene
                scene_parser = PydanticOutputParser(pydantic_object=StoryGeneratorResponse)
                new_scene = scene_parser.parse(result.content)
                new_scenes[idx] = new_scene
                print(f"✅ Regenerated scene {idx}: {new_scene.scene}")
        
        return StoryListResponse(scenes=new_scenes)
    except Exception as e:
        print(f"Error regenerating specific scenes: {e}")
        return existing_story


def regenerate_single_image(scene: StoryGeneratorResponse, output_dir: str) -> ImageGeneratorResponse:
    """
    Regenerate a single image for a specific scene.
    
    Args:
        scene: Scene data with prompts
        output_dir: Directory to save the image
    
    Returns:
        ImageGeneratorResponse with the new image path
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        client_nebius = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=settings.NEBIUS_API_KEYS
        )
        
        prompt_text = scene.prompts[0] if scene.prompts else scene.visual_cues
        scene_title_safe = scene.scene.replace(' ', '_').replace(':', '')
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        image_filename = os.path.join(output_dir, f"{scene_title_safe}_{unique_id}.png")
        
        print(f"🎨 Regenerating image for scene: {scene.scene}")
        
        # Generate image
        response = client_nebius.images.generate(
            model="black-forest-labs/flux-dev",
            prompt=prompt_text,
        )
        
        image_url = getattr(response.data[0], "url", None)
        if not image_url:
            raise ValueError("No image URL returned by API.")
        
        # Download image
        image_response = requests.get(image_url, stream=True)
        image_response.raise_for_status()
        
        with open(image_filename, 'wb') as file:
            for chunk in image_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"✅ Image saved: {image_filename}")
        
        # Create response object
        scene_dict = scene.model_dump()
        scene_dict["image"] = image_filename
        return ImageGeneratorResponse(**scene_dict)
        
    except Exception as e:
        print(f"❌ Error regenerating image: {e}")
        return None


def regenerate_single_video(image_scene: ImageGeneratorResponse, output_dir: str) -> VideoGeneratorResponse:
    """
    Regenerate a single video clip for a specific scene.
    
    Args:
        image_scene: Scene with image reference
        output_dir: Directory to save the video
    
    Returns:
        VideoGeneratorResponse with the new video path
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        safe_title = image_scene.scene.replace(" ", "_").replace(":", "")
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(output_dir, f"{safe_title}_{unique_id}.mp4")
        
        video_scene = VideoGeneratorResponse(
            scene=image_scene.scene,
            narration=image_scene.narration,
            visual_cues=image_scene.visual_cues,
            prompts=image_scene.prompts,
            image=image_scene.image,
            video_path=None,
        )
        
        uploaded_file = None
        
        try:
            # Upload reference image if available
            if image_scene.image and os.path.exists(image_scene.image):
                print(f"📤 Uploading reference image: {image_scene.image}")
                uploaded_file = client.files.upload(file=image_scene.image)
            
            # Configure video generation
            config_kwargs = {
                "duration_seconds": 4,
                "aspect_ratio": "16:9",
            }
            if uploaded_file:
                config_kwargs["reference_images"] = [uploaded_file]
            config = types.GenerateVideosConfig(**config_kwargs)
            
            # Generate video
            print(f"🎬 Regenerating video for scene: {image_scene.scene}")
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=image_scene.visual_cues,
                config=config,
            )
            
            # Poll until complete
            print("⏳ Waiting for video generation...")
            while not operation.done:
                print(".", end="", flush=True)
                time.sleep(10)
                operation = client.operations.get(operation.name)
            
            # Download video
            if getattr(operation, "response", None) and getattr(operation.response, "generated_videos", None):
                generated_video = operation.response.generated_videos[0]
                client.files.download(file=generated_video.video, output_path=output_path)
                video_scene.video_path = output_path
                print(f"\n✅ Video saved: {output_path}")
            else:
                print(f"\n❌ Video generation failed")
                
        finally:
            # Cleanup
            if uploaded_file:
                try:
                    client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass
        
        return video_scene
        
    except Exception as e:
        print(f"❌ Error regenerating video: {e}")
        return None


def regenerate_single_voiceover(scene: VideoGeneratorResponse, output_dir: str = "voice_overs") -> VideoWithVoiceoverResponse:
    """
    Regenerate voiceover for a single scene.
    
    Args:
        scene: Scene with narration text
        output_dir: Directory to save voiceover
    
    Returns:
        VideoWithVoiceoverResponse with new voiceover path
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        unique_id = str(uuid.uuid4())[:8]
        tts_path = os.path.join(
            output_dir,
            f"{scene.scene.replace(' ', '_').replace(':', '')}_{unique_id}.mp3"
        )
        
        print(f"🎤 Regenerating voiceover for scene: {scene.scene}")
        
        tts = gTTS(text=scene.narration, lang='en', slow=False)
        tts.save(tts_path)
        
        scene_dict = scene.model_dump()
        scene_dict["voiceover"] = tts_path
        result = VideoWithVoiceoverResponse(**scene_dict)
        
        print(f"✅ Voiceover saved: {tts_path}")
        return result
        
    except Exception as e:
        print(f"❌ Error regenerating voiceover: {e}")
        return None

