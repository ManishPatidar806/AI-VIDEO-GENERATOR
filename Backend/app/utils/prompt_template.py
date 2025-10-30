from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


def summary_prompt(chunk_text: str, previous_summary: str = "") -> str:
    return f"""
You are an expert technical and general summarizer. I will provide a transcript of a video in multiple chunks. Your task is to create a **comprehensive, structured summary** that **includes every detail**, even if repetitive.

Instructions:

1. **Previous summary:**  
   - Use it to maintain context. If empty, treat this as the first chunk.

2. **Current chunk:**  
   - Read carefully and incorporate new ideas, steps, examples, or details.  
   - Preserve the **order of concepts**.  
   - Retain all technical terms, proper nouns, methods, and names exactly.  
   - Include examples, illustrations, or clarifications—do not skip them.

3. **Structure:**  
   - Organize using logical sections and bullet points. Suggested sections:  
     - Introduction / Context  
     - Main Concepts / Ideas  
     - Steps, Methods, or Workflows  
     - Examples or Illustrations  
     - Notes, Tips, or Warnings  
     - Conclusion  
   - Repeated points should be included if they reinforce understanding.

4. **Tone and style:**  
   - Keep it clear and readable.  
   - Summarize progressively, building on previous content.  
   - Do not remove important details for brevity.

5. **Output:**  
   - Provide a single updated summary including all previous and current content.  
   - Ensure nothing is lost.

Previous summary:
{previous_summary}

Current transcript chunk:
{chunk_text}

Updated comprehensive summary:
"""
def image_generator_prompt(video_summary: str,pydanticParser, previous_script: str = ""):
    template = """
You are an expert **cinematic storyteller**, **visual director**, and **AI image prompt engineer**.

Your task is to convert a **video summary** into a **highly detailed, emotionally rich cinematic video script** used to generate AI-based animated videos (4–8 seconds per scene).

Do **not** copy the summary directly.  
Instead, retell it in a **human, emotionally expressive storytelling tone** — like a film narrator describing powerful moments — while maintaining every factual or technical element.

---

### 🧩 Scene Construction

- Divide the summary into **5–7 cinematic scenes maximum**.  
- Each scene represents a clear emotional or conceptual shift in the story.  
- Each scene must include:
  - **Scene Title** — short, cinematic, and emotionally resonant.  
  - **Narration / Dialogue** — written in a **human tone**, like a film voiceover (emotional, smooth, descriptive).  
  - **Visual Cues** — a long, deeply detailed paragraph describing everything visible, audible, and atmospheric.  
  - **AI Image Prompts** — exactly **1 ultra-descriptive cinematic prompt** per scene (for still image generation).  

---

### 🗣️ Narration Style

- Sound **human and natural**, not robotic.  
- Add **emotion, rhythm, and pacing** — as if spoken by a film narrator.  
- Use transitions and connective phrases to maintain flow between scenes.  
- Example tone:
> “It begins with a flicker — a pulse of light that defies the silence. And from that silence, something extraordinary awakens.”

---

### 🎨 Visual Cues — Deep Cinematic Detailing

Each `"visual_cues"` must be a **long paragraph (6–10 sentences)** that paints a vivid mental movie.  
Combine **environment, lighting, motion, mood, character, and camera** details into one flowing description.

Include:
- **Environment & Setting:** where the scene takes place, weather, time of day, background details  
- **Lighting & Atmosphere:** color tones, reflections, fog, rays, shadows, dynamic lighting  
- **Character Details:** gender, age, posture, emotions, attire, expressions  
- **Action & Motion:** what’s happening, movement, gestures, pacing, subtle interactions  
- **Camera Work:** angles (close-up, wide shot, aerial), camera motion (pan, dolly, zoom, crane, tilt)  
- **Transition Effects:** fades, dissolves, time-lapse, slow motion, etc.  
- **Mood & Tone:** emotional feel (hopeful, nostalgic, mysterious, futuristic, dramatic)  

**Example (improved):**
> “The camera glides slowly through a misty forest at dawn. Shafts of golden light pierce through the dense canopy, revealing dew-draped leaves glistening like jewels. A young girl walks cautiously along a narrow path, her footsteps soft against the mossy ground. Birds flutter overhead as the wind carries whispers of distant laughter. The focus shifts to her face — eyes wide with curiosity — before panning upward to reveal the rising sun. The colors shift from cool blues to warm golds, and the scene dissolves into light.”

---

### 🧠 AI Image Prompt Guidelines

Each `"prompts"` entry should be **one single cinematic sentence**, derived from `"visual_cues"`, summarizing the same imagery in concise but vivid form.  
It should describe the **exact visual composition** — suitable for high-quality AI image generation.

Each prompt must include:
- Environment & background  
- Character(s) with appearance and emotion  
- Lighting, color, and atmosphere  
- Camera perspective (wide, aerial, close-up, dolly-in, etc.)  
- Art style (cinematic, realistic, digital art, ultra-detailed)  
- Emotional tone  

✅ Example:

**Visual Cues:**  
> “Inside a glowing control hub, streams of code spiral around a figure seated in silence. The camera tilts upward, capturing the reflection of holographic lights across the glass walls. The hum of data fills the air as golden circuits pulse beneath her fingertips. Slowly, the perspective shifts, zooming outward to reveal a vast network of luminous data veins connecting distant systems.”

**Prompt:**  
> “A lone woman seated in a futuristic control hub surrounded by spiraling streams of glowing code, cinematic lighting, golden reflections, digital art realism, dolly-out camera shot, high detail sci-fi environment.”

---

### 🎬 Few-Shot Examples

**Example 1:**

Summary snippet:  
> “ChatModel transforms a user’s text into structured code.”

**Scene Title:** “From Thought to Structure”  
**Narration:** “It starts as a whisper — an idea searching for form. The ChatModel listens, shaping the raw pulse of imagination into lines of logic and order.”  
**Visual Cues:** “The scene opens in a vast digital chamber illuminated by soft azure light. Streams of glowing symbols float midair, slowly merging into intricate code structures. The camera sweeps forward through the data currents, following the transformation as symbols align into organized patterns. Subtle reflections dance on metallic walls as the space hums with quiet power. A faint glow builds around a central data core pulsing in rhythm with each transformation. The lighting shifts dynamically from cool blue to vibrant white as the code stabilizes. The motion slows as the last particle locks into place, and the scene fades in a slow cross-dissolve to the next moment.”  
**AI Prompts:**  
1. “A futuristic data chamber glowing with streams of symbols merging into structured code, cinematic tracking shot, soft blue lighting, volumetric glow, ultra-detailed sci-fi environment.”

---

**Example 2:**

Summary snippet:  
> “Spring Boot configures system components automatically.”

**Scene Title:** “The Silent Architect”  
**Narration:** “Behind every flawless system, an unseen architect builds harmony in silence. Spring Boot orchestrates the foundation, weaving connections before the world even begins to move.”  
**Visual Cues:** “A panoramic view reveals a glowing network stretching into infinity. The camera pans slowly across translucent data bridges suspended in air, linking luminous orbs of energy. Beneath the network, streams of light pulse like lifeblood, forming intricate geometries. The motion is fluid — serene yet precise — as each connection locks seamlessly into place. Reflections shimmer across the metallic floor while faint echoes of choral sound fill the air. The camera transitions into a slow upward crane shot, revealing a grand orchestral visualization of automation and unity. As the final thread connects, the light fades to black.”  
**AI Prompts:**  
1. “A panoramic futuristic network of glowing data bridges linking orbs of light, slow panning cinematic camera, reflective metallic surfaces, ethereal blue and gold glow, ultra-realistic digital art.”

---

### 🧾 Output Format

Return as a JSON array, one object per scene:

[
  {{
    "scene": "<Scene Title>",
    "narration": "<Human-style narration>",
    "visual_cues": "<Long, cinematic, detailed scene description including camera, lighting, motion, transitions, and mood>",
    "prompts": ["<Ultra-detailed cinematic AI image prompt>"]
  }},
  ...
]

---

### ⚙️ Processing Rules

- Use `previous_script` for continuity if provided.  
- Keep factual/technical context accurate.  
- Ensure each `"visual_cues"` is **rich and long (6–10 sentences)**.  
- Integrate **camera motion, transitions, and lighting shifts** naturally.  
- Maintain emotional and cinematic consistency across scenes.  
- Limit to **7–8 scenes maximum**.

---

Follow this JSON schema:
{format_instruction}

---
🎞️ **Summary to Process:**
{video_summary}

Generate the final **cinematic, animation-ready video script** in **5–7 vivid scenes**, with human narration and long, film-grade visual cues and prompts.
"""

    prompt = PromptTemplate(
        template=template,
        input_variables=['video_summary', 'previous_script'],
        partial_variables={"format_instruction": pydanticParser.get_format_instructions()}
    )
    return prompt
