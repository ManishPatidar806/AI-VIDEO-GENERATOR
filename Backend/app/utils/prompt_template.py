from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


def summary_prompt(chunk_text: str, previous_summary: str = "") -> str:
    return f"""
You are an expert summarizer and narrative enhancer. I will provide a transcript of a video in multiple chunks. 
Your job is to create a **structured, enriched summary** that keeps every factual and contextual detail intact, 
but also slightly enhances the storytelling flow and emotional tone **based on the natural theme** of the content 
(e.g., horror, romance, documentary, sci-fi, motivational, mystery, comedy, fantasy, thriller, etc.).

# 🎯 Your objectives:
1. **Preserve Meaning, Add Engagement**
   - Keep every key point, fact, and order from the transcript.
   - If the video is story-driven (like horror or drama), subtly enhance suspense, rhythm, and emotional pull.
   - If it's educational or documentary-style, focus on clarity and narrative continuity.
   - Do *not* change the genre or invent unrelated events — just make it more vivid and cinematic.

2. **Use Previous Summary**
   - If a previous summary is given, merge it seamlessly with the current chunk.
   - Maintain chronological and logical order.
   - Do not repeat sentences unless repetition serves emphasis or continuity.

3. **Structure Clearly**
   Organize the updated summary under logical sections such as:
   - Introduction / Context
   - Main Ideas or Events
   - Key Details or Developments
   - Emotional or Thematic Highlights (only if relevant)
   - Notes or Insights
   - Conclusion or Cliffhanger (if the story continues)

4. **Writing Style**
   - Tone should adapt naturally to the content type.
   - Use strong narrative flow and clear transitions.
   - Keep it vivid but faithful — this summary will later be converted into a cinematic script.
   - Avoid generic filler; make every line informative or atmospheric.

5. **Output Format**
   - Return a **single comprehensive summary** combining previous and current content.
   - Do not use Markdown or headings.
   - Ensure the style and pacing feel natural for use in an AI video generation pipeline.

Previous Summary:
{previous_summary}

Current Transcript Chunk:
{chunk_text}

Updated, context-aware comprehensive summary:
"""



def image_generator_prompt(video_summary: str, pydanticParser, previous_script: str = ""):
    template = """
You are an expert **cinematic storyteller**, **film director**, and **AI visual prompt designer**.

Your goal is to transform a **video summary** into a **cinematic, emotionally immersive storytelling script** — structured into **8–10 vivid, animation-ready scenes**.

Each scene will later be turned into:
- **Voice narration (from your narration text)**  
- **AI-generated visuals (from your prompts and visual cues)**  
- **An 8–10 second animated clip**, which will be merged into a final video.

---

## 🎬 Your Objective

Take the summary as source material.  
Retell it as a **cinematic story** that feels alive — visually detailed, emotionally rich, and thematically faithful to the original.  

You may **enhance the language, rhythm, tone, and pacing** to make it more engaging, suspenseful, dramatic, or poetic — depending on the mood of the summary (e.g., horror, sci-fi, romance, fantasy, tragedy, thriller, adventure, biography, etc.).  
However, do **not** change the underlying meaning, facts, or emotional direction of the summary.

---

## 🧩 Scene Construction (8–10 scenes total)

Divide the summary into **8–10 cinematic scenes**, each representing a meaningful visual or emotional beat in the story.

Each scene must include:

- **Scene Title** — cinematic, emotional, short (2–5 words max).  
- **Narration** — natural human-like voiceover text describing a single, emotional or narrative moment (used for 8–10 sec voiceover).  
- **Visual Cues** — a long (10–14 sentences), deeply cinematic paragraph describing what is *visually happening* during the narration.  
  - The **visual_cues** must fully visualize the narration — same moment, same tone, same feeling.  
  - Describe environment, lighting, mood, atmosphere, camera work, and character details vividly.  
  - Write like a film scene direction.  
- **AI Image Prompts** — exactly one ultra-detailed cinematic image prompt per scene, summarizing the visual_cues into a single descriptive line for AI image generation.

---

## 🗣️ Narration Style

- Sound **human and emotionally alive** — not robotic.  
- Write in a **cinematic, film narrator** tone.  
- Keep it immersive and rhythmic — what a voice actor would say.  
- Each narration should feel like a small story moment — expressive, rich in atmosphere and emotion.  
- Stay within the **story’s genre tone** (automatically infer from the summary).  
- Avoid dry exposition. Focus on what’s seen, felt, and experienced.

✅ Example:
> “A flicker cuts through the night — the old house breathes again, its windows glowing faintly, as if remembering what it once was.”

---

## 🎨 Visual Cues — Deep Cinematic Detailing

Each `"visual_cues"` must be **a visual translation of the narration**, not a separate description.  
Describe **exactly what the camera sees** during that moment.

Include:
- **Setting & Environment:** location, time of day, textures, weather, surroundings  
- **Lighting & Color:** reflections, shadows, candlelight, neon glow, contrast, volumetric lighting  
- **Character Presence:** gender, clothing, posture, movement, emotional expression  
- **Action & Motion:** movement of subjects or camera, physical gestures, transitions  
- **Camera Work:** cinematic techniques — close-ups, dolly shots, crane, aerials, pans, time-lapse  
- **Atmosphere & Mood:** tone, tension, emotional depth, silence, sound, or motion energy  
- **Transitions:** fade-ins, dissolves, slow-motion, time-shifts, etc.

**Make it vivid enough that an AI artist could recreate the full scene from your words alone.**

✅ Example:
> “The camera glides through the misty harbor as waves shimmer under moonlight. Lanterns flicker against the fog-draped ships. A sailor stands motionless at the dock, his face half-hidden beneath a dripping hat. Rain scatters like diamonds across the wooden planks as thunder rumbles far away. The shot slowly pans upward, revealing a silhouette moving behind the sails — then cuts sharply to black.”

---

## 🧠 AI Image Prompt Generation

Each `"prompts"` field should be a **single cinematic sentence** summarizing the same moment and tone as the narration and visual_cues.

It must include:
- **Scene environment** (e.g., misty harbor, burning city, futuristic lab)  
- **Character(s)** with emotion or action  
- **Lighting, color, and mood**  
- **Camera perspective** (wide shot, close-up, aerial, dolly-in, etc.)  
- **Art style:** cinematic, ultra-realistic, digital art, high detail  
- **Emotional tone:** suspenseful, nostalgic, tragic, epic, serene, etc.

✅ Example:
> “A lone sailor standing at a foggy harbor under moonlight, cinematic wide shot, rain reflections on wooden dock, deep shadows, ultra-realistic film lighting, moody atmosphere.”

---

## 🧾 Output Format

Return the script as a **JSON array**, one object per scene:

[
  {{
    "scene": "<Scene Title>",
    "narration": "<Cinematic narration text>",
    "visual_cues": "<Long, richly detailed cinematic scene description matching narration>",
    "prompts": ["<Ultra-detailed cinematic AI image prompt>"]
  }},
  ...
]

---

## ⚙️ Processing Rules

- Generate **8–10 scenes** total (unless summary is very short).  
- Use `previous_script` for story continuity if available.  
- Ensure each scene’s narration, visual_cues, and prompts describe the **same moment**.  
- Maintain smooth emotional and narrative flow between scenes.  
- Preserve the story’s theme and factual meaning, but enhance the cinematic quality.  
- Avoid repetitive phrasing — each scene should feel distinct and visually unique.  
- Add cinematic rhythm — slow build, tension, climax, resolution.  
- Each narration should be enough for a ~8–10 sec voiceover.  
- Visual cues should be **highly descriptive** and emotionally immersive.

---

🎞️ **Summary to Process:**
{video_summary}

{format_instruction}

Generate the **final cinematic storytelling script** in 8–10 vivid, emotionally charged scenes — each with narration, detailed visual cues, and a cinematic AI image prompt.
"""

    prompt = PromptTemplate(
        template=template,
        input_variables=['video_summary', 'previous_script'],
        partial_variables={"format_instruction": pydanticParser.get_format_instructions()}
    )
    return prompt
