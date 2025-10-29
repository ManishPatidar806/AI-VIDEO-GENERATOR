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
        # return TranscriptUploadResponse(message="NO CONTENT FOUND OR NO TRANSCRIPT FOUND",status=404,success=False)
        return "No content found"
    except Exception:
        # return TranscriptUploadResponse(message="Video is Not Available",status=404,success=False)   
        return "Video is not availabel"


# ! Video Script Generator
def story_generator(summary:str):
    try:
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',google_api_key=settings.GOOGLE_API_KEY , temperature=1.2) 
        prompt = image_generator_prompt(summary)
        formatted_prompt = prompt.format(
        video_summary=summary,
        )
        result = llm.invoke(formatted_prompt)
        parsed_output = pydanticParser.parse(result.content)
        return parsed_output
    except Exception:
        print(Exception)
        print("Somthing went worng in story generator script")    



# ! Image  Generator
def image_generate(scenes: List["StoryGeneratorResponse"], output_dir: str) -> List["ImageGeneratorResponse"]:
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
def video_generation(images: List["ImageGeneratorResponse"], output_dir: str = "generated_videos") -> List["VideoGeneratorResponse"]:
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
            image=image.image_path,
            video_path=None,
        )

        try:
            # --- 1️⃣ Upload reference image if available ---
            if image.image_path and os.path.exists(image.image_path):
                print(f"\n📤 Uploading reference image: {image.image_path}")
                uploaded_file = client.files.upload(file=image.image_path)
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
        scene_with_voiceover = ImageWithVoiceoverResponse(**scene_dict)
        
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
    scenes_with_images = image_generate(scenes=story_scenes, output_dir=OUTPUT_DIR)

    if not scenes_with_images:
        print("❌ No images generated. Aborting pipeline.")
        return None

    # --- Step 2: Generate Video Clips (Veo 3.1) ---
    # The Veo function uses the prompts/images from the previous step to create video clips.
    # We must define a new directory for the videos to avoid mixing with reference images.
    VIDEO_CLIPS_DIR = "generated_videos" 
    os.makedirs(VIDEO_CLIPS_DIR, exist_ok=True)
    print(f"\n🎥 STEP 2: Generating video clips for all scenes (using Veo 3.1 in {VIDEO_CLIPS_DIR})...")
    scenes_with_videos = video_generation(
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
    scenes_with_voiceovers = generate_voiceover(scenes_with_videos=scenes_with_videos)

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

# Generate story from video summary
video_summary = transcript_generator(videoId="-XFmbnGtCas")
story_response = story_generator(summary=video_summary)
print(story_response.model_dump_json(indent=2))


# Run complete pipeline 
final_video = complete_video_pipeline(story_scenes=story_response.scenes, output_video_name="my_video.mp4")

    # scenes=[StoryGeneratorResponse(scene='The Genesis of Thought', narration="We've carefully crafted the fundamental blocks: intricate messages, specific chat options, and the universal prompt. But a profound truth lingers: our eloquently constructed prompt, while understood by our system, remains an alien whisper to the formidable digital titans like OpenAI or Anthropic. Our true quest, our bridge-building endeavor, culminates in the ChatModel. This intelligent interpreter takes our raw intention, meticulously shapes it into the precise dialect each AI comprehends, and launches it into the digital ether. It's a marvel of seamless integration, gracefully manifesting its specific form within our Spring framework based on the very foundations of our project's dependencies.", visual_cues="A programmer, deep in thought, surrounded by glowing lines of code. The generic 'prompt' appears as a luminous orb, floating mystically. As narration mentions AI providers, stylized icons for OpenAI, Anthropic, and Mistral AI flicker into existence around the orb. The 'ChatModel' interface appears as a ghostly blueprint, then solidifies into a specific implementation like 'OpenAIChatModel' depending on a 'pom.xml' snippet. Focus on transformation and connectivity, futuristic workspace, low-key lighting.", prompts=["A glowing, generic prompt orb transforming into specific AI provider symbols (OpenAI, Anthropic, Mistral AI), with a 'ChatModel' blueprint materializing from code lines in a futuristic coding environment. Cinematic lighting, deep focus, digital art."]), StoryGeneratorResponse(scene='The Polyglot Gatekeepers', narration="Imagine an elite assembly of specialized translators, each possessing perfect fluency in the unique tongue of a specific AI giant. These are our concrete ChatModel implementations: the `OpenAIChatModel`, the `AnthropicChatModel`, and the `MistralAIChatModel`, among others. Each stands as a dedicated guardian, taking that universally understood prompt and meticulously sculpting it into the exact request object their particular AI demands. They don't just translate; they possess the inherent knowledge of *how* to knock on the right digital door, *which* specific API to call, and how to patiently await the `ChatResponse`—the AI's insightful reply. And should you choose not to articulate specific preferences, worry not, for they are designed to gracefully defer to wise default options.", visual_cues="A row of distinct, stylized AI portals (one for OpenAI, one for Anthropic, etc.), each glowing with a unique color scheme. Each portal is guarded by a cloaked, enigmatic figure representing its specific 'ChatModel' implementation. A generic prompt symbol, pulsating with energy, moves towards the OpenAI guardian, who then expertly crafts a glowing, OpenAI-specific request object before sending it into the portal. Emphasize specificity, responsibility, and arcane digital craftsmanship.", prompts=['A row of futuristic, stylized AI portals (OpenAI, Anthropic, Mistral AI), each guarded by a distinct cloaked figure with glowing eyes. A generic glowing data packet approaches, and an OpenAI guardian transforms it into a complex, provider-specific data structure before launching it into the OpenAI portal. Cinematic, digital art, high contrast.']), StoryGeneratorResponse(scene="The Solo Maestro's Symphony", narration="Let's witness the elegant flow when our system speaks primarily to one intelligence. From a simple `/api/ai/chat` endpoint, a discreet whisper in our controller reaches the ears of our service. Here, the `ChatModel` patiently awaits, seamlessly woven into the fabric of our application by Spring Boot’s benevolent, auto-configuration hand. If OpenAI is our sole confidant, Spring will unfailingly present the `OpenAIChatModel`, ready to orchestrate our list of messages, configure nuanced options like temperature and token limits, and bundle them into a comprehensive `Prompt` object. With a swift invocation, `chatModel.call(prompt)`, our message embarks on its journey, silently translated and conveyed, returning an eloquent `ChatResponse`.", visual_cues="A sleek visual representation of an API call flowing from a web browser interface, through a minimalist controller screen, into a service method represented by a focused processing core. A single, illuminated 'OpenAIChatModel' object glows prominently as it's injected. Data packets representing 'List<Message>' and 'ChatOption' converge and morph to form a unified, shimmering 'Prompt' object. The 'Prompt' then swiftly moves towards the 'OpenAIChatModel', which emits a vibrant 'ChatResponse' back to the service. Clean, flowing animation of data, tech aesthetic.", prompts=["An animated data flow showing a request from a futuristic browser interface to a minimalist controller, then to a Spring Boot service core. A glowing 'OpenAIChatModel' bean is seamlessly injected, receiving input messages and options, bundling them into a vibrant 'Prompt' object, and generating a dynamic 'ChatResponse'. High-tech, seamless motion graphics."]), StoryGeneratorResponse(scene='The Conclave of Cognition', narration="But what if our ambition stretches further, embracing a diverse council of intelligences? When your `pom.xml` proudly houses both OpenAI and Anthropic dependencies, Spring, ever so generous, meticulously prepares beans for *both* `OpenAIChatModel` and `AnthropicChatModel`. This generosity, however, creates a delightful dilemma: which `ChatModel` to inject when a generic request arrives? Spring cannot simply guess. This is where clarity and precision prevail. With the sacred `@Qualifier` annotation, we explicitly instruct Spring, naming our desired agent—be it `openAIChatModel` or `anthropicChatModel`. Our application's pathways, too, must diverge: a distinct endpoint for OpenAI, another for Anthropic, each channeling requests to their designated, expertly qualified AI companion.", visual_cues="Two distinct, glowing 'ChatModel' beans (one labeled 'OpenAI', one 'Anthropic') appear side-by-side on a futuristic console, causing a shimmering 'conflict' icon to pulse between them. A developer's hand inputs code snippets onto the console, showing `@Qualifier` annotations appearing next to variable declarations, resolving the conflict. Simultaneously, two separate API routes (visualized as distinct, branching digital pathways) emerge from the console, each leading to its respective AI model, glowing with unique identifier colors. Emphasize choice, precision, and strategic programming.", prompts=["Two glowing AI ChatModel beans (OpenAIChatModel, AnthropicChatModel) on a futuristic console, causing a shimmering conflict symbol to pulse. Code showing '@Qualifier' annotations appears to resolve the ambiguity. Two separate digital pathways (API routes) emerge, each leading to its distinct AI provider. High-tech, conceptual art, dynamic light."]), StoryGeneratorResponse(scene="The Oracle's Many Tongues", narration="The `ChatModel` interface itself is a virtuoso, a master of many voices and entry points. It offers a `call(String)` method, a simpler path where you merely whisper a query like 'What is Java?' The model, in its wisdom, silently crafts a `Prompt` and engages the AI. Then there’s `call(List<Message>)`, designed for richer, multi-turn conversations, accepting a tapestry of thoughts. Yet, at the very core of every specific ChatModel implementation lies the abstract `call(Prompt)` method. This is where the magic truly happens—the crucible where our comprehensive `Prompt`, carrying all its messages and options, is finally transmuted into an AI-specific request, the ultimate invocation to the digital oracle, and the awaited `ChatResponse` emerges.", visual_cues="A majestic, ancient-looking 'ChatModel' interface symbol, carved from digital light, with three glowing conduits extending from it, representing `call(String)`, `call(List<Message>)`, and `call(Prompt)`. The `call(String)` conduit shows a simple text input transforming into a complex 'Prompt' object within. The `call(List<Message>)` conduit shows multiple flowing message streams merging into a 'Prompt'. The central `call(Prompt)` conduit highlights intricate internal conversion processes, showing data morphing, leading to an external API call and a radiant 'ChatResponse' appearing at its end. Mythical, magical tech, glowing runes.", prompts=["A majestic, ancient-looking 'ChatModel' interface symbol carved from digital light, with three glowing conduits: one showing simple text transforming into a 'Prompt', another showing a list of messages merging into a 'Prompt', and the central conduit depicting intricate internal data conversion of the 'Prompt' into an AI-specific request, culminating in a radiant 'ChatResponse'. Mythical tech, glowing runes, cinematic."]), StoryGeneratorResponse(scene='The Proving Grounds', narration="With our multi-faceted ChatModels deployed and meticulously configured, the true test of their capabilities begins. Imagine making a crucial call to Anthropic, only to receive a stark 'insufficient credit' error – a poignant testament that our application successfully connected, but met a real-world financial barrier. Then, with a swift pivot, a simple 'Hello, how are you?' sent to OpenAI, and instantaneously, a warm, intelligent response flows back. This isn't mere theory; it's a live symphony of integration, demonstrating the undeniable power to seamlessly switch between the titans of AI, each configured with its unique keys, each answering to its designated ChatModel. The stage is now perfectly set for next time, when we delve into the profound secrets held within that `ChatResponse` itself.", visual_cues="A dynamic split-screen showing two distinct command-line terminals. On one, an Anthropic API call command is executed, swiftly returning a stark 'Insufficient credit' error message that pulses with a vibrant red glow. On the other, an OpenAI API call command is executed, and within moments, a successful, friendly AI response appears, glowing with a serene green light. A confident programmer leans back, a subtle smile playing on their lips, acknowledging the success. The scene then transitions, focusing on a highly detailed, glowing 'ChatResponse' icon, hinting at the next episode. Cinematic, high-tech aesthetic.", prompts=["Split screen showing two distinct command-line interfaces: one displaying a 'connection denied/insufficient credit' error message for Anthropic AI (pulsing red glow), the other displaying a successful, friendly AI response from OpenAI (serene green glow). A confident developer in the background, subtly smiling. Futuristic tech office, cinematic lighting, high-contrast."])]
    # ,output_dir=OUTPUT_DIR))





# print(assemble_final_video([ImageGeneratorResponse(scene='The Genesis of Thought', narration="We've carefully crafted the fundamental blocks: intricate messages, specific chat options, and the universal prompt. But a profound truth lingers: our eloquently constructed prompt, while understood by our system, remains an alien whisper to the formidable digital titans like OpenAI or Anthropic. Our true quest, our bridge-building endeavor, culminates in the ChatModel. This intelligent interpreter takes our raw intention, meticulously shapes it into the precise dialect each AI comprehends, and launches it into the digital ether. It's a marvel of seamless integration, gracefully manifesting its specific form within our Spring framework based on the very foundations of our project's dependencies.", visual_cues="A programmer, deep in thought, surrounded by glowing lines of code. The generic 'prompt' appears as a luminous orb, floating mystically. As narration mentions AI providers, stylized icons for OpenAI, Anthropic, and Mistral AI flicker into existence around the orb. The 'ChatModel' interface appears as a ghostly blueprint, then solidifies into a specific implementation like 'OpenAIChatModel' depending on a 'pom.xml' snippet. Focus on transformation and connectivity, futuristic workspace, low-key lighting.", prompts=["A glowing, generic prompt orb transforming into specific AI provider symbols (OpenAI, Anthropic, Mistral AI), with a 'ChatModel' blueprint materializing from code lines in a futuristic coding environment. Cinematic lighting, deep focus, digital art."], image='nebius_scene_images/1_The_Genesis_of_Thought.png'), ImageGeneratorResponse(scene='The Polyglot Gatekeepers', narration="Imagine an elite assembly of specialized translators, each possessing perfect fluency in the unique tongue of a specific AI giant. These are our concrete ChatModel implementations: the `OpenAIChatModel`, the `AnthropicChatModel`, and the `MistralAIChatModel`, among others. Each stands as a dedicated guardian, taking that universally understood prompt and meticulously sculpting it into the exact request object their particular AI demands. They don't just translate; they possess the inherent knowledge of *how* to knock on the right digital door, *which* specific API to call, and how to patiently await the `ChatResponse`—the AI's insightful reply. And should you choose not to articulate specific preferences, worry not, for they are designed to gracefully defer to wise default options.", visual_cues="A row of distinct, stylized AI portals (one for OpenAI, one for Anthropic, etc.), each glowing with a unique color scheme. Each portal is guarded by a cloaked, enigmatic figure representing its specific 'ChatModel' implementation. A generic prompt symbol, pulsating with energy, moves towards the OpenAI guardian, who then expertly crafts a glowing, OpenAI-specific request object before sending it into the portal. Emphasize specificity, responsibility, and arcane digital craftsmanship.", prompts=['A row of futuristic, stylized AI portals (OpenAI, Anthropic, Mistral AI), each guarded by a distinct cloaked figure with glowing eyes. A generic glowing data packet approaches, and an OpenAI guardian transforms it into a complex, provider-specific data structure before launching it into the OpenAI portal. Cinematic, digital art, high contrast.'], image='nebius_scene_images/2_The_Polyglot_Gatekeepers.png'), ImageGeneratorResponse(scene="The Solo Maestro's Symphony", narration="Let's witness the elegant flow when our system speaks primarily to one intelligence. From a simple `/api/ai/chat` endpoint, a discreet whisper in our controller reaches the ears of our service. Here, the `ChatModel` patiently awaits, seamlessly woven into the fabric of our application by Spring Boot’s benevolent, auto-configuration hand. If OpenAI is our sole confidant, Spring will unfailingly present the `OpenAIChatModel`, ready to orchestrate our list of messages, configure nuanced options like temperature and token limits, and bundle them into a comprehensive `Prompt` object. With a swift invocation, `chatModel.call(prompt)`, our message embarks on its journey, silently translated and conveyed, returning an eloquent `ChatResponse`.", visual_cues="A sleek visual representation of an API call flowing from a web browser interface, through a minimalist controller screen, into a service method represented by a focused processing core. A single, illuminated 'OpenAIChatModel' object glows prominently as it's injected. Data packets representing 'List<Message>' and 'ChatOption' converge and morph to form a unified, shimmering 'Prompt' object. The 'Prompt' then swiftly moves towards the 'OpenAIChatModel', which emits a vibrant 'ChatResponse' back to the service. Clean, flowing animation of data, tech aesthetic.", prompts=["An animated data flow showing a request from a futuristic browser interface to a minimalist controller, then to a Spring Boot service core. A glowing 'OpenAIChatModel' bean is seamlessly injected, receiving input messages and options, bundling them into a vibrant 'Prompt' object, and generating a dynamic 'ChatResponse'. High-tech, seamless motion graphics."], image="nebius_scene_images/3_The_Solo_Maestro's_Symphony.png"), ImageGeneratorResponse(scene='The Conclave of Cognition', narration="But what if our ambition stretches further, embracing a diverse council of intelligences? When your `pom.xml` proudly houses both OpenAI and Anthropic dependencies, Spring, ever so generous, meticulously prepares beans for *both* `OpenAIChatModel` and `AnthropicChatModel`. This generosity, however, creates a delightful dilemma: which `ChatModel` to inject when a generic request arrives? Spring cannot simply guess. This is where clarity and precision prevail. With the sacred `@Qualifier` annotation, we explicitly instruct Spring, naming our desired agent—be it `openAIChatModel` or `anthropicChatModel`. Our application's pathways, too, must diverge: a distinct endpoint for OpenAI, another for Anthropic, each channeling requests to their designated, expertly qualified AI companion.", visual_cues="Two distinct, glowing 'ChatModel' beans (one labeled 'OpenAI', one 'Anthropic') appear side-by-side on a futuristic console, causing a shimmering 'conflict' icon to pulse between them. A developer's hand inputs code snippets onto the console, showing `@Qualifier` annotations appearing next to variable declarations, resolving the conflict. Simultaneously, two separate API routes (visualized as distinct, branching digital pathways) emerge from the console, each leading to its respective AI model, glowing with unique identifier colors. Emphasize choice, precision, and strategic programming.", prompts=["Two glowing AI ChatModel beans (OpenAIChatModel, AnthropicChatModel) on a futuristic console, causing a shimmering conflict symbol to pulse. Code showing '@Qualifier' annotations appears to resolve the ambiguity. Two separate digital pathways (API routes) emerge, each leading to its distinct AI provider. High-tech, conceptual art, dynamic light."], image='nebius_scene_images/4_The_Conclave_of_Cognition.png'), ImageGeneratorResponse(scene="The Oracle's Many Tongues", narration="The `ChatModel` interface itself is a virtuoso, a master of many voices and entry points. It offers a `call(String)` method, a simpler path where you merely whisper a query like 'What is Java?' The model, in its wisdom, silently crafts a `Prompt` and engages the AI. Then there’s `call(List<Message>)`, designed for richer, multi-turn conversations, accepting a tapestry of thoughts. Yet, at the very core of every specific ChatModel implementation lies the abstract `call(Prompt)` method. This is where the magic truly happens—the crucible where our comprehensive `Prompt`, carrying all its messages and options, is finally transmuted into an AI-specific request, the ultimate invocation to the digital oracle, and the awaited `ChatResponse` emerges.", visual_cues="A majestic, ancient-looking 'ChatModel' interface symbol, carved from digital light, with three glowing conduits extending from it, representing `call(String)`, `call(List<Message>)`, and `call(Prompt)`. The `call(String)` conduit shows a simple text input transforming into a complex 'Prompt' object within. The `call(List<Message>)` conduit shows multiple flowing message streams merging into a 'Prompt'. The central `call(Prompt)` conduit highlights intricate internal conversion processes, showing data morphing, leading to an external API call and a radiant 'ChatResponse' appearing at its end. Mythical, magical tech, glowing runes.", prompts=["A majestic, ancient-looking 'ChatModel' interface symbol carved from digital light, with three glowing conduits: one showing simple text transforming into a 'Prompt', another showing a list of messages merging into a 'Prompt', and the central conduit depicting intricate internal data conversion of the 'Prompt' into an AI-specific request, culminating in a radiant 'ChatResponse'. Mythical tech, glowing runes, cinematic."], image="nebius_scene_images/5_The_Oracle's_Many_Tongues.png"), ImageGeneratorResponse(scene='The Proving Grounds', narration="With our multi-faceted ChatModels deployed and meticulously configured, the true test of their capabilities begins. Imagine making a crucial call to Anthropic, only to receive a stark 'insufficient credit' error – a poignant testament that our application successfully connected, but met a real-world financial barrier. Then, with a swift pivot, a simple 'Hello, how are you?' sent to OpenAI, and instantaneously, a warm, intelligent response flows back. This isn't mere theory; it's a live symphony of integration, demonstrating the undeniable power to seamlessly switch between the titans of AI, each configured with its unique keys, each answering to its designated ChatModel. The stage is now perfectly set for next time, when we delve into the profound secrets held within that `ChatResponse` itself.", visual_cues="A dynamic split-screen showing two distinct command-line terminals. On one, an Anthropic API call command is executed, swiftly returning a stark 'Insufficient credit' error message that pulses with a vibrant red glow. On the other, an OpenAI API call command is executed, and within moments, a successful, friendly AI response appears, glowing with a serene green light. A confident programmer leans back, a subtle smile playing on their lips, acknowledging the success. The scene then transitions, focusing on a highly detailed, glowing 'ChatResponse' icon, hinting at the next episode. Cinematic, high-tech aesthetic.", prompts=["Split screen showing two distinct command-line interfaces: one displaying a 'connection denied/insufficient credit' error message for Anthropic AI (pulsing red glow), the other displaying a successful, friendly AI response from OpenAI (serene green glow). A confident developer in the background, subtly smiling. Futuristic tech office, cinematic lighting, high-contrast."], image='nebius_scene_images/6_The_Proving_Grounds.png')]))