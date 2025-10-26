from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import List
from langchain_core.prompts import PromptTemplate

videoId = "dZqa_9H803w"

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',google_api_key=settings.GOOGLE_API_KEY)




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

class StoryGeneratorResponse(BaseModel):
    scene: str = Field(..., description="The title of the scene")
    narration: str = Field(..., description="The creative narration or dialogue for this scene")
    visual_cues: str = Field(..., description="Detailed description of visuals, characters, environment, and mood")
    prompts: List[str] = Field(..., description="List of AI image generation prompts for this scene")

class StoryListResponse(BaseModel):
    scenes: List[StoryGeneratorResponse]


pydanticParser = PydanticOutputParser(pydantic_object=StoryListResponse)
def image_generator_prompt(video_summary :str,previous_script:str = ""):
    template = """
You are an expert creative video script writer and AI image prompt engineer. 
Your task is to convert a **summary of a video** into a **cinematic, engaging video script** with visual storytelling. 
Do **not** copy the summary word-for-word. Instead, rephrase, dramatize, and creatively interpret the content while preserving all key technical points, proper nouns, methods, examples, and workflows.

Instructions:

1️⃣ Scene Creation
- Break the summary into **logical scenes**.
- Each scene should include:
  - **Scene Title**: Short, descriptive, catchy.
  - **Narration / Dialogue**: Rephrase the summary creatively for narration, dialogue, or monologue.
  - **Visual Cues**: Describe characters, objects, environment, camera angles, lighting, action, and mood.
  - **AI Image Prompts**: 2–4 prompts per scene for generating visuals; each prompt should cover different perspectives, styles, or moods of the scene.

2️⃣ Tone and Style
- Make the script **engaging, cinematic, and story-driven**.
- Use metaphors, analogies, examples, or illustrative scenarios where appropriate.
- Introduce emotion, suspense, or humor creatively while staying technically accurate.
- Preserve the **flow of ideas** from the summary.

3️⃣ Few-Shot Examples
Example 1:
Summary snippet: "OpenAI ChatModel converts a generic prompt to a provider-specific request object."
Scene:
Scene Title: "The Transformation of the Prompt"
Narration: "Imagine a universal message magically transforming into a secret code that only OpenAI can understand. The ChatModel, our hero, reshapes this message into the perfect AI request."
Visual Cues: "Glowing scroll morphing into digital code, futuristic AI interface, cinematic lighting."
AI Prompts:
1. "A glowing scroll transforming into digital code, futuristic AI interface, cinematic lighting"
2. "Fantasy-style magical scroll morphing into futuristic holographic data, neon accents"
3. "Close-up of hands typing code on floating holographic interface, digital glow"
4. "Animated sequence showing text transforming into AI-understandable format"

Example 2:
Summary snippet: "Spring Boot auto-configures OpenAIChatModel and OpenAIChatOption beans."
Scene:
Scene Title: "Spring Boot Magic"
Narration: "Watch as Spring Boot waves its magic wand and instantly, the ChatModel and its options appear, ready for action—no manual setup required!"
Visual Cues: "Magical sparkles, glowing code snippets, futuristic office background."
AI Prompts:
1. "Digital interface appearing magically with glowing sparkles, futuristic office, cinematic style"
2. "Magic wand casting glowing digital code, AI configuration appearing, bright ambient lighting"
3. "Futuristic spring-themed UI forming automatically, sparkles and holographic effects"
4. "Cinematic animation of software components auto-configuring with magical glow"

4️⃣ Output Format
Return the script as a JSON array, one object per scene:

[
  {{
    "scene": "<Scene Title>",
    "narration": "<Creative narration or dialogue>",
    "visual_cues": "<Scene visuals, characters, environment, mood>",
    "prompts": ["<AI image prompt 1>", "<AI image prompt 2>", "<AI image prompt 3>", "<AI image prompt 4>"]
  }},
  ...
]

5️⃣ Processing Instructions
- Build on any **previous script** if provided to maintain continuity.
- Ensure **no technical details or important content are lost** while adding creative elements.
- Avoid repeating the summary verbatim; transform it into cinematic storytelling.

Follow the JSON schema format exactly as described below:
{format_instruction}
---
Summary:
{video_summary}
Generate the **updated creative video script**, including new scenes and modifications necessary for continuity.
"""
    
    prompt =  PromptTemplate(
        template=template,
        input_variables=['video_summary', 'previous_script'],
        partial_variables={"format_instruction": pydanticParser.get_format_instructions()}
    )
    return prompt
    

def story_generator(summary:str):
    # try:
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',google_api_key=settings.GOOGLE_API_KEY , temperature=1.2) 
        prompt = image_generator_prompt(summary)
        formatted_prompt = prompt.format(
        video_summary=summary,
        )
        result = llm.invoke(formatted_prompt)
        print("---- Raw LLM Output ----")
        print("\n---- Parsed JSON ----")
        parsed_output = pydanticParser.parse(result.content)
        return parsed_output
    # except Exception:
    #     print(Exception)
    #     print("Somthing went worng in story generator script")    

story_generator("""Here is the updated comprehensive summary based on the provided transcript chunk:

Introduction / Context

   The video features a 22-year-old YouTuber revealing his income, with Ash reacting to this information.
   A news headline is referenced, stating, "Last month I made 35 LS news headline times of H you are not alone."
   The speaker is Isan Sharma, who is currently 23 years old.
   Isan shares his personal transformation journey: he went from being a "broke 18-year-old" in college who knew nothing about life, was deeply underconfident, shy, lacked skills, and "cannot talk to a girl," to a 23-year-old who now interviews billionaires, travels the world, and possesses the financial freedom to support not only himself but also his parents.
   He describes his story as an "outlier story" that received media attention a couple of weeks prior.
   The primary purpose of this video is to explain how his experience and the power of content creation can also help the viewer.
   Isan validates his lessons and steps by sharing his own journey and achievements: in the last 5 years, he has made over 1,000 videos on YouTube and gained over 250 million views.

Main Concepts / Ideas

   Ubiquity of Content Creation: Isan posits that "every around us are content creators." He argues that if someone shares content on Instagram for 48 hours, even if only to a private number of friends, they are a content creator. The key difference lies in sharing content with "everyone out there" rather than a private audience.
   The True Power of Content Creation (for Isan Sharma): He clarifies that the real benefits for him are not superficial perks like "free business class tickets" or "followers coming around me wanting a picture." Instead, the profound advantages include:
       The freedom to work from wherever he wants.
       The freedom to work on whatever he wants.
       The opportunity to meet "incredible people" that he could never otherwise meet as a 23-year-old.
   Content Creation as a Modern Career Path: Isan notes a significant shift in career aspirations; while kids traditionally wanted to be astronauts, today they aspire to become content creators. Despite its widespread popularity, he observes that "no one really talks about how do you become a Creator like how can you get started."
   Accessibility of Content Creation (No Need to be Full-Time): Isan emphasizes that one does not need to be a "full-time Creator." He himself is not a full-time creator; he runs a marketing agency and engages in content creation "on the side."
       Content creation can be pursued by individuals who are working a job, running a business, or working as a freelancer.
       The process involves documenting one's journey, sharing lessons learned, and building a personal name or brand for oneself.
   Addressing the "Nothing to Share" Concern: Isan references an Ali Abdal quote: "what's obvious to you is amazing to others." This means that everyone possesses talents and skills that might seem obvious to them but could be "amazing" or an "eye opener" for others. The goal is to find that one thing and be known for it.
   Leveraging AI in Content Creation: Creating content alone can feel overwhelming, but "smartest creators" use AI to their advantage. AI can help make the process faster than ever, assisting with:
       Idea generation.
       Scripting.
       Generating crisp audio.
       AI video.
       Ultra-realistic images.
       A free guide by HubSpot, titled "using generative AI to scale your content operations guide," can help viewers get started. This guide contains numerous ways to use AI throughout the content pipeline, from generating unique ideas to helping with research and repurposing content.
       The guide also highlights various nuances of AI, such as the possibilities of biases in AI-driven content and the risk of plagiarism with generative AI.
       Isan personally appreciates the part of the guide that delves into various ways to use AI to improve team productivity.

Steps, Methods, or Workflows

   This video is designed to help viewers get started with content creation.
   Within the "next 10 minutes," Isan plans to share "five very important steps that can help you get to your first YouTube video" and "to your first Instagram real."
   Step 1: Find Your One Word / Niche
       The objective is to discover "that one word that your audience can replace your name with" or "what word are you synonymous with."
       This involves identifying "that one thing that you can specialize over" and that people can relate you with (e.g., about coding, or other specific topics).
       It is easier to be known for "one thing" than to try "generalize trying to be known for everything out there."
       Examples of Niche Specialization:
           Productivity: Ali Abdal
           Motivation in India: Sandeep Maheshwari
           Freelancing in India: Isan Sharma
   Step 2: Forget the Tools and Build the Muscle
       This step addresses the common tendency for people to wait for "that nice camera, that nice light, that nice background, that nice mic or equipment."
       Isan emphasizes that "you don't need any of it."
       Sufficient tools are already available to most viewers: "If you're watching this YouTube video right now you have a laptop or you have a mobile phone or you have a tablet. These are enough tools that you can use to start recording."
       He advises against needing "fancy equipment."
       Isan shares his personal experience: his first few videos "were not highly produced" and he "was using a two megapixel front camera of my laptop."
       The core advice is to "forget the tools," as "no one cares about you," and instead to "just get started, get that foot in the door, just shoot."
       The focus should be on building the "muscle" to "sit every day in front of a non-living thing called camera and shoot," talking about what you are interested in "every single day."
       This daily practice of talking to the camera helps build the "muscle" to easily create content.
       An analogy is provided: "just like a pair of Nike shoes will not turn you into a runner if you yourself don't have that habit, the best tools in the world will not help you become the best Creator if you don't have it inside of you if you have not build that muscle inside."
   Step 3: Find Your Style
       Isan observes that many people he meets, whose content (e.g., a reel) he reviews, appear to be "pretending to be someone else" and don't seem "genuine."
       This lack of genuineness indicates that the person is copying someone else and not being themselves, which is identified as a "big problem."
       Every major successful creator is an "anomaly," meaning they are "one of zero" or "one of a kind." They all "differentiate themselves."
       Conversely, "every failed Creator or someone who does not get views is not able to differentiate from the competition."
       It is crucial to "find out your style." Examples of personal style include:
           Someone who "loves to talk with typography on the screen" should "do that," showing people how to convey a story with typography.
           Someone who "loves to just talk and be raw in front of the camera" should "do that."
       Viewers should not copy successful creators like Mr. Beast, even if he gets "hundreds of millions of views."
       The advice is to "do what works for you," "do what builds your own authentic Unique Style," and "stop copying."
       Copying will "never get you to success, especially in the field of content creation," because "it's a zero-sum game."
       People have limited attention ("only 24 ads") and will "only consume the top 1% creators," so "only they will succeed."
       Therefore, "you have to stand out." If you do not, you will "end up just becoming one of the many, one of the millions of creators who copy each other and end up becoming mediocre."
       "Finding your style" encompasses "the way you edit a video, the storytelling that you have, how humorous are you, how serious are you, what language you're talking in." Everything falls "Under the Umbrella of finding your Unique Style."
   Step 4: Build a Cult
       This step emphasizes the need to "build a cult," drawing an analogy to past cult leaders who "used to hypnotize Their audience into believing something to be truth."
       Every successful creator was able to create a cult.
       In this context, a "cult" refers to "a series of people who are dedicated to a belief or a thought process that you circulate as a Creator."
       This could be a specific mentality, a particular thought process, an opinion, or a belief that others can relate with.
       Isan Sharma's personal example of a "hot take" is to "focus more on skills over degrees," stating that "a degree is not going to get you to the right place in life, a skill however can take you places."
       If an audience member agrees with this belief, they become "a part of my cult" and "carry that belief and hence me and my identity in your heart."
       These supporters then "sort of become a supporter of this belief and you now try to spread this belief to as many people as possible."
       The ultimate goal is for the cult to grow on its own, "getting people together, getting people in this community automatically."
       Isan recommends watching a "brilliant documentary on Netflix which talks about how do you become a cult leader" to learn how it works and apply those learnings to content creation.

Key Skills for Content Creation

   Effective Writing: Writing is a foundational skill that creators will "keep coming back to again and again" throughout their entire creation journey, whether for video scripts, reel scripts, or any other content.
       It is essential for capturing the attention of people with "goldfish memory."
       Improving writing skills helps people "immediately stick to what you have to say" and encourages them to share the content.
       Mastering writing, including using "right hooks," telling a "beautiful story," and incorporating the "right CTA" (Call To Action) at the end, is key to success in content creation.

Notes, Tips, or Warnings

   Isan is sharing "what took me 5 years to learn in the next 10 minutes," highlighting the condensed value of the information.
   Patience (Bonus Tip): Content creation requires patience. "Rome was not built in a day," and growth takes time.
       An analogy is provided with the Chinese bamboo tree, which requires 5 years of consistent daily watering, showing no visible growth. After these 5 years, it then grows 90 feet tall in the next two weeks. This illustrates that consistent effort might not show immediate results but builds a strong foundation, emphasizing that the growth is a result of the full 5 years of effort, not just the two weeks.
   Content creators must "keep experimenting," "be open to ideas," and "unlearn before you learn."
   A "free guide by HubSpot that will help you become a better content creator using AI" will be shared for those who watch till the end. This guide is specifically named "HubSpot's using generative AI to scale your content operations guide" and is available via a link in the description.

Conclusion

   The video aims to provide practical guidance and actionable steps for individuals interested in starting their content creation journey, specifically targeting the creation of their initial YouTube video and Instagram reel.
   The journey to content creation is described as "very simple," involving five steps focused on execution and learning.
   The ultimate benefits of this journey include impacting millions of people, achieving financial independence, and successfully creating a cult that believes in the creator's core beliefs.
   Viewers are encouraged to "hit the like button and subscribe" if the content is valuable.
   Viewers are asked to provide feedback in the comment section if they learned anything from the video.
   For those who watched till the very end, Isan requests a specific comment: "I watch till the very end."
   Viewers are also invited to take a screenshot of the video, post it on Instagram, and tag Isan Sharma (@isan Sharma 7390).
   Isan concludes by stating he will see the audience "again in the next one.""")

