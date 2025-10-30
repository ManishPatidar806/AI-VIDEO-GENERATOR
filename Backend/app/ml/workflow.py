from langgraph.graph import StateGraph, Start, End
from app.schemas.ml_process_response import VideoWithVoiceoverResponse
from app.ml.model_connect import story_generator,video_generator,assemble_final_video,transcript_generator,image_generator,generate_voiceover
from app.schemas.ml_process_response import VideoWithVoiceoverResponse


workflow = StateGraph(VideoWithVoiceoverResponse)
workflow.add_node('transcript_generator',transcript_generator)
workflow.add_node("story_generator", story_generator)
workflow.add_node("image_generator", image_generator)
workflow.add_node("video_generator", video_generator)
workflow.add_node("voice_generator", generate_voiceover)
workflow.add_node("assemble_final_video",assemble_final_video)





