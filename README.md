<div align="center">

# 🎬 AI Video Generator

### Automated Video Creation from YouTube Transcripts

[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.1-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0.2-121212?style=for-the-badge)](https://langchain.com/)

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [ML Pipeline](#-ml-pipeline)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**AI Video Generator** is an enterprise-grade, full-stack application that transforms YouTube video transcripts into professionally produced short-form videos. Leveraging cutting-edge AI technologies including LangChain, Google Generative AI, and advanced video processing libraries, this platform automates the entire video creation workflow from transcript extraction to final video assembly.

### 🎯 Key Highlights

- 🤖 **AI-Powered Content Generation**: Utilizes Google Generative AI for intelligent story generation and scene creation
- 🎨 **Automated Image Generation**: Creates contextual images for each scene using advanced AI models
- 🎙️ **Voice-Over Synthesis**: Generates natural-sounding voice-overs using Google Text-to-Speech (gTTS)
- 🔄 **Flexible Regeneration**: Regenerate any component (story, scenes, images, videos) independently
- 📊 **Project Management**: Track and manage multiple video projects with session-based workflows
- 🔐 **Secure Authentication**: JWT-based authentication with password hashing
- 🎬 **Professional Video Assembly**: Combines images, voice-overs, and effects into polished final videos

---

## ✨ Features

### Core Features

#### 🎥 Video Generation Pipeline
- **YouTube Transcript Extraction**: Automatically fetch and process YouTube video transcripts
- **AI Story Generation**: Transform transcripts into engaging narrative structures
- **Scene Breakdown**: Intelligent scene segmentation with optimized timing
- **Image Generation**: Create contextual images for each scene
- **Voice-Over Creation**: Generate synchronized voice narration
- **Video Assembly**: Combine all elements into a cohesive final video

#### 🔄 Regeneration & Customization
- **Story Regeneration**: Regenerate story structure while maintaining transcript context
- **Selective Scene Regeneration**: Regenerate specific scenes independently
- **Image Regeneration**: Update images for individual or multiple scenes
- **Video Regeneration**: Re-render videos with updated assets
- **Voice-Over Regeneration**: Regenerate audio narration
- **Batch Operations**: Regenerate multiple assets simultaneously

#### 🛠️ Advanced Features
- **Scene Modification**: Edit scene descriptions, prompts, and timing
- **Image Modification**: Update image prompts and regenerate
- **Project Sessions**: Manage multiple video projects concurrently
- **Asset Management**: Organized storage and retrieval of generated assets
- **Progress Tracking**: Real-time status updates during generation
- **Error Handling**: Robust error recovery and retry mechanisms

### User Features

#### 🔐 Authentication & Authorization
- User registration and login
- JWT token-based authentication
- Secure password hashing with Argon2
- Protected routes and API endpoints

#### 📊 Project Management
- Create and manage multiple video projects
- Session-based workflow tracking
- View project history and details
- Download generated videos

#### 🎨 User Interface
- Modern, responsive design with Tailwind CSS
- Component library powered by Radix UI
- Dark/Light theme support
- Step-by-step guided workflow
- Real-time progress indicators

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React + TypeScript)            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Landing Page  │  Auth  │  Dashboard  │  Video Studio   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                         Axios HTTP Client                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                          REST API (FastAPI)
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                      Backend (FastAPI + Python)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Routes  │  Auth Service  │  ML Pipeline  │  DB     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌──────────────────────────┴────────────────────────────┐     │
│  │            LangGraph AI Workflow Pipeline              │     │
│  │  ┌──────────────────────────────────────────────────┐ │     │
│  │  │  Transcript → Story → Images → Videos → Assemble │ │     │
│  │  └──────────────────────────────────────────────────┘ │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
           ┌────────┴────────┐   ┌───────┴────────┐
           │  PostgreSQL DB   │   │  File Storage  │
           │  (SQLModel)      │   │  (Images/Videos)│
           └──────────────────┘   └────────────────┘
```

### ML Pipeline Workflow

```
YouTube URL
    │
    ▼
┌─────────────────────┐
│ Transcript Extractor│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Story Generator    │ ◄── Google Generative AI
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Scene Generator    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Image Generator    │ ◄── Nebius AI / Image API
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Voice Generator    │ ◄── gTTS (Google TTS)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Video Generator    │ ◄── MoviePy
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Final Assembler    │
└──────────┬──────────┘
           │
           ▼
    Final Video MP4
```

---

## 💻 Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.119.1 | High-performance async web framework |
| **Python** | 3.11+ | Core programming language |
| **SQLModel** | 0.0.27 | SQL databases with Python type annotations |
| **PostgreSQL** | - | Primary relational database |
| **LangChain** | 1.0.2 | LLM orchestration framework |
| **LangGraph** | 1.0.1 | State machine workflow for AI pipelines |
| **Google Generative AI** | 3.0.0 | AI content generation |
| **MoviePy** | Latest | Video editing and processing |
| **gTTS** | Latest | Google Text-to-Speech |
| **Pydantic** | 2.12.3 | Data validation using Python type annotations |
| **SQLAlchemy** | 2.0.44 | SQL toolkit and ORM |
| **Uvicorn** | 0.38.0 | ASGI server |
| **PyJWT** | 2.10.1 | JSON Web Token implementation |
| **Argon2-cffi** | 25.1.0 | Password hashing |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI library |
| **TypeScript** | 5.8.3 | Type-safe JavaScript |
| **Vite** | 5.4.19 | Build tool and dev server |
| **React Router** | 6.30.1 | Client-side routing |
| **TanStack Query** | 5.83.0 | Server state management |
| **Axios** | 1.13.1 | HTTP client |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS framework |
| **Radix UI** | Latest | Headless UI components |
| **Shadcn/ui** | Latest | Re-usable component library |
| **Framer Motion** | 12.23.24 | Animation library |
| **React Hook Form** | 7.61.1 | Form handling |
| **Zod** | 3.25.76 | Schema validation |
| **Lucide React** | 0.462.0 | Icon library |

### AI & ML Services

- **Google Generative AI (Gemini)**: Story and scene generation
- **Nebius AI**: Image generation
- **YouTube Transcript API**: Transcript extraction
- **Google TTS**: Voice synthesis

---

## 📋 Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm** or **bun**: Latest version
- **PostgreSQL**: 14.x or higher
- **Git**: For version control

### API Keys Required

You'll need to obtain the following API keys:

1. **Google API Key** (for Generative AI)
   - Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)
   
2. **Nebius API Key** (for image generation)
   - Get from: [Nebius Platform](https://nebius.ai/)

3. **PostgreSQL Database**
   - Local installation or cloud service (e.g., Supabase, ElephantSQL)

---

## 🚀 Installation

### Backend Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR.git
cd AI-VIDEO-GENERATOR/Backend
```

#### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Environment Configuration

Create a `.env` file in the `Backend` directory:

```bash
touch .env
```

Add the following environment variables:

```env
# Application Settings
APP_NAME=AI-Video-Generator
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_video_db

# API Keys
GOOGLE_API_KEY=your_google_api_key_here
NEBIUS_API_KEYS=your_nebius_api_key_here

# Optional: Sentry for error tracking
SENTRY_DNS=your_sentry_dns_here

# Security (if implementing custom JWT)
# JWT_SECRET=your_secret_key_here
# JWT_ALGORITHM=HS256
```

#### 5. Database Setup

```bash
# Create PostgreSQL database
createdb ai_video_db

# Or using psql
psql -U postgres
CREATE DATABASE ai_video_db;
\q
```

The database tables will be automatically created on first run.

#### 6. Create Required Directories

```bash
mkdir -p generated_images generated_videos nebius_scene_images voice_overs
```

#### 7. Run the Backend Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The backend API will be available at `http://localhost:8000`

#### 8. Verify Installation

```bash
curl http://localhost:8000
# Should return: {"message":"AI-Video-Generator is running!"}
```

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd ../Frontend
```

#### 2. Install Dependencies

```bash
# Using npm
npm install

# Using bun (faster)
bun install
```

#### 3. Environment Configuration

Create a `.env` file in the `Frontend` directory:

```bash
touch .env
```

Add the following:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

#### 4. Run Development Server

```bash
# Using npm
npm run dev

# Using bun
bun run dev
```

The frontend will be available at `http://localhost:5173`

#### 5. Build for Production

```bash
# Using npm
npm run build

# Using bun
bun run build
```

The production build will be in the `dist` directory.

---

## ⚙️ Configuration

### Backend Configuration

The backend configuration is managed through `Backend/app/core/config.py` using Pydantic settings:

```python
class Settings(BaseSettings):
    APP_NAME: str = 'TranscriptApplication'
    DEBUG: bool = False
    GOOGLE_API_KEY: str
    SENTRY_DNS: str | None = None
    ALLOWED_HOSTS: list[str] = ["*"]
    DATABASE_URL: str
    NEBIUS_API_KEYS: str
```

### Frontend Configuration

Frontend configuration is managed through environment variables and Vite:

- **API Base URL**: Set in `.env` as `VITE_API_BASE_URL`
- **Build Configuration**: `vite.config.ts`
- **TypeScript Configuration**: `tsconfig.json`
- **Tailwind Configuration**: `tailwind.config.ts`

### CORS Configuration

CORS is configured in `Backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_methods=["*"],
    allow_headers=["*"]
)
```

⚠️ **Production Note**: Update `allow_origins` to specific domains in production.

---

## 📖 Usage

### Step-by-Step Workflow

#### 1. User Registration/Login

1. Navigate to `http://localhost:5173/auth`
2. Create an account or login
3. Upon successful authentication, you'll be redirected to the dashboard

#### 2. Create New Video Project

1. From the dashboard, click "Create New Project"
2. Enter a YouTube URL
3. The system will extract the transcript

#### 3. Generate Story & Scenes

1. Review the extracted transcript
2. Click "Generate Story" to create an AI-generated narrative
3. The system will automatically break down the story into scenes

#### 4. Generate Images

1. Review the generated scenes
2. Click "Generate Images" to create visuals for each scene
3. Regenerate individual images if needed

#### 5. Generate Videos

1. Once images are ready, click "Generate Videos"
2. The system will create video clips with voice-overs
3. Review and regenerate if necessary

#### 6. Final Assembly

1. Click "Assemble Final Video"
2. The system combines all elements into the final video
3. Download your completed video

### API Usage Example

```bash
# 1. Register User
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123","name":"John Doe"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'

# 3. Generate Transcript (with JWT token)
curl -X POST http://localhost:8000/api/v1/generate/transcript \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"videoId":"dQw4w9WgXcQ"}'
```

---

## 📚 API Documentation

### Authentication Endpoints

#### `POST /api/v1/auth/signup`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGc..."
}
```

#### `POST /api/v1/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Generation Endpoints

#### `POST /api/v1/generate/transcript`
Extract transcript from YouTube video.

**Request Body:**
```json
{
  "videoId": "dQw4w9WgXcQ"
}
```

#### `POST /api/v1/generate/story`
Generate story from transcript.

#### `POST /api/v1/generate/images`
Generate images for all scenes.

#### `POST /api/v1/generate/videos`
Generate video clips with voice-overs.

#### `POST /api/v1/generate/final-video`
Assemble final video from all components.

### Regeneration Endpoints

#### `POST /api/v1/regenerate/story`
Regenerate the story structure.

#### `POST /api/v1/regenerate/specific-scenes`
Regenerate specific scenes by scene numbers.

**Request Body:**
```json
{
  "session_id": 123,
  "scene_numbers": [1, 3, 5]
}
```

#### `POST /api/v1/regenerate/image`
Regenerate image for a specific scene.

#### `POST /api/v1/regenerate/video`
Regenerate video for a specific scene.

#### `POST /api/v1/regenerate/voiceover`
Regenerate voice-over for a specific scene.

#### `POST /api/v1/regenerate/batch-regenerate/images`
Batch regenerate multiple images.

#### `POST /api/v1/regenerate/batch-regenerate/videos`
Batch regenerate multiple videos.

### Update Endpoints

#### `PUT /api/v1/regenerate/update/scene`
Update scene details (description, prompt, timing).

**Request Body:**
```json
{
  "scene_id": 1,
  "narration": "Updated scene description",
  "image_prompt": "Updated image prompt",
  "duration": 5.0
}
```

#### `POST /api/v1/regenerate/modify-scene`
Modify scene with new instructions.

#### `POST /api/v1/regenerate/modify-image`
Modify image with new prompt.

### API Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

---

## 📁 Project Structure

### Backend Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── auth_router.py            # Authentication endpoints
│   │           ├── transcript_generate_route.py  # Generation endpoints
│   │           └── transcript_regenerate_route.py # Regeneration endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                # Application configuration
│   ├── db/
│   │   ├── init_db.py              # Database initialization
│   │   └── session.py              # Database session management
│   ├── ml/
│   │   ├── model_connect.py        # ML model connections
│   │   ├── text.py                 # Text processing utilities
│   │   └── workflow.py             # LangGraph workflow definition
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py           # User model
│   │   ├── videoSessions_model.py  # Video session model
│   │   ├── storygenerate_model.py  # Story generation model
│   │   ├── summaries_model.py      # Scene/summary model
│   │   ├── images.py               # Image model
│   │   └── video.py                # Video model
│   ├── schemas/
│   │   ├── api_response.py         # API response schemas
│   │   ├── ml_process_response.py  # ML process schemas
│   │   ├── transcript_request.py   # Request schemas
│   │   └── user.py                 # User schemas
│   ├── services/                   # Business logic services
│   └── utils/
│       ├── prompt_template.py      # AI prompt templates
│       └── security.py             # Security utilities (JWT, hashing)
├── generated_images/               # Generated image storage
├── generated_videos/               # Generated video storage
├── nebius_scene_images/           # Nebius AI generated images
├── voice_overs/                   # Voice-over audio files
├── requirements.txt               # Python dependencies
├── showData.json                  # Sample/test data
└── testData.json                  # Test data
```

### Frontend Structure

```
Frontend/
├── public/
│   └── robots.txt
├── src/
│   ├── components/
│   │   ├── Logo.tsx
│   │   ├── ProjectCard.tsx         # Project display card
│   │   ├── ProtectedRoute.tsx      # Route protection wrapper
│   │   ├── StepProgress.tsx        # Progress indicator
│   │   ├── landing/                # Landing page components
│   │   │   ├── CTA.tsx
│   │   │   ├── Demo.tsx
│   │   │   ├── Features.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── HowItWorks.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── Testimonials.tsx
│   │   └── ui/                     # Shadcn/UI components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── form.tsx
│   │       ├── input.tsx
│   │       └── ...                 # 50+ UI components
│   ├── contexts/
│   │   └── AuthContext.tsx         # Authentication context
│   ├── hooks/
│   │   ├── use-mobile.tsx          # Mobile detection hook
│   │   └── use-toast.ts            # Toast notification hook
│   ├── lib/
│   │   ├── api.ts                  # API client configuration
│   │   └── utils.ts                # Utility functions
│   ├── pages/
│   │   ├── Auth.tsx                # Authentication page
│   │   ├── CompletePipeline.tsx    # Full pipeline view
│   │   ├── Home.tsx                # Dashboard
│   │   ├── LandingPage.tsx         # Public landing page
│   │   ├── NotFound.tsx            # 404 page
│   │   ├── ProjectDetail.tsx       # Individual project view
│   │   ├── Projects.tsx            # Projects list
│   │   ├── Step1Summarize.tsx      # Transcript & story step
│   │   ├── Step2Prompts.tsx        # Scene prompts step
│   │   ├── Step3Images.tsx         # Image generation step
│   │   └── Step4Video.tsx          # Video generation step
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # Application entry point
│   └── index.css                   # Global styles
├── components.json                 # Shadcn/UI configuration
├── package.json                    # Node dependencies
├── tsconfig.json                   # TypeScript configuration
├── vite.config.ts                  # Vite configuration
└── tailwind.config.ts              # Tailwind CSS configuration
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram


### Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### VideoSessions Table
```sql
CREATE TABLE video_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    youtube_url VARCHAR(500) NOT NULL,
    transcript_text TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### StoryGenerate Table
```sql
CREATE TABLE story_generate (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES video_sessions(id),
    story_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Summaries Table
```sql
CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES video_sessions(id),
    scene_number INTEGER NOT NULL,
    narration TEXT NOT NULL,
    image_prompt TEXT,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Images Table
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    summary_id INTEGER REFERENCES summaries(id),
    image_url VARCHAR(500),
    prompt TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### GeneratedVideo Table
```sql
CREATE TABLE generated_video (
    id SERIAL PRIMARY KEY,
    video_session_id INTEGER REFERENCES video_sessions(id),
    video_url VARCHAR(500),
    resolution VARCHAR(50),
    duration_sec INTEGER,
    video_prompt TEXT,
    images_url JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🤖 ML Pipeline

### LangGraph Workflow

The ML pipeline is implemented using LangGraph, providing a stateful workflow:

```python
workflow = StateGraph(VideoWithVoiceoverResponse)

# Define nodes
workflow.add_node('transcript_generator', transcript_generator)
workflow.add_node('story_generator', story_generator)
workflow.add_node('image_generator', image_generator)
workflow.add_node('video_generator', video_generator)
workflow.add_node('voice_generator', generate_voiceover)
workflow.add_node('assemble_final_video', assemble_final_video)
```

### Pipeline Components

#### 1. Transcript Generator
- Extracts transcript from YouTube using `youtube-transcript-api`
- Cleans and formats transcript text
- Stores in database

#### 2. Story Generator
- Uses Google Generative AI (Gemini)
- Transforms transcript into engaging narrative
- Applies storytelling techniques
- Maintains key information

#### 3. Scene Generator
- Breaks story into optimized scenes
- Calculates timing for each scene
- Generates image prompts
- Creates narration text

#### 4. Image Generator
- Generates contextual images using Nebius AI
- Falls back to alternative image generation if needed
- Stores images locally
- Validates image quality

#### 5. Voice-Over Generator
- Converts narration to speech using gTTS
- Adjusts pacing and timing
- Generates audio files
- Syncs with scene duration

#### 6. Video Generator
- Combines images and audio using MoviePy
- Adds transitions and effects
- Optimizes video quality
- Generates MP4 files

#### 7. Final Assembler
- Combines all scene videos
- Adds intro/outro (optional)
- Applies final effects
- Generates final deliverable

### Prompt Templates

Prompts are managed in `Backend/app/utils/prompt_template.py`:

```python
STORY_GENERATION_PROMPT = """
Transform the following transcript into an engaging story...
"""

SCENE_BREAKDOWN_PROMPT = """
Break down the story into {num_scenes} scenes...
"""

IMAGE_GENERATION_PROMPT = """
Generate a detailed image prompt for: {scene_description}
"""
```

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd Backend
pytest

# Frontend tests
cd Frontend
npm run test
```

### Code Formatting

```bash
# Backend (Python)
black app/
isort app/
flake8 app/

# Frontend (TypeScript)
npm run lint
npm run format
```

### Development Tools

- **Backend Debugging**: Use VS Code Python debugger or `pdb`
- **Frontend Debugging**: React DevTools, Browser DevTools
- **API Testing**: Postman, Thunder Client, or Swagger UI
- **Database Management**: pgAdmin, DBeaver, or psql

### Hot Reload

Both backend and frontend support hot reload:

- **Backend**: Enabled with `--reload` flag
- **Frontend**: Enabled by default with Vite

---

## 🚢 Deployment

### Backend Deployment

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t ai-video-generator-backend .
docker run -p 8000:8000 --env-file .env ai-video-generator-backend
```

#### Using Platform Services

##### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create ai-video-generator-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set NEBIUS_API_KEYS=your_key

# Deploy
git push heroku main
```

##### Railway / Render
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically from main branch

### Frontend Deployment

#### Build for Production

```bash
cd Frontend
npm run build
# or
bun run build
```

#### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

#### Deploy to Static Hosting

Upload the `dist` folder to:
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps
- GitHub Pages

### Environment Variables for Production

Update production environment variables:

```env
# Backend
DATABASE_URL=your_production_db_url
DEBUG=False
ALLOWED_HOSTS=["yourdomain.com"]

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

### SSL/HTTPS

Ensure HTTPS is enabled:
- Use Let's Encrypt for free SSL certificates
- Configure reverse proxy (Nginx, Caddy)
- Use platform-provided SSL (Vercel, Netlify)

---

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

**Issue: Database connection error**
```
Solution: Verify DATABASE_URL in .env file
- Check PostgreSQL is running: pg_isready
- Verify credentials and database exists
```

**Issue: Google API quota exceeded**
```
Solution: 
- Check API usage in Google Cloud Console
- Implement rate limiting
- Use caching for repeated requests
```

**Issue: Image generation fails**
```
Solution:
- Verify NEBIUS_API_KEYS is correct
- Check API service status
- Implement fallback image generation
```

**Issue: Video assembly fails**
```
Solution:
- Ensure MoviePy dependencies installed: ffmpeg
- Check disk space for temp files
- Verify file permissions on storage directories
```

#### Frontend Issues

**Issue: CORS error**
```
Solution: Update CORS settings in Backend/app/main.py
- Add specific origin instead of "*"
- Verify backend URL in Frontend .env
```

**Issue: Build fails**
```
Solution:
- Clear node_modules: rm -rf node_modules && npm install
- Update dependencies: npm update
- Check Node version compatibility
```

**Issue: Authentication not persisting**
```
Solution:
- Check localStorage in browser DevTools
- Verify JWT token expiration
- Check axios interceptor configuration
```

### Debug Mode

Enable debug logging:

```python
# Backend - in .env
DEBUG=True

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

```typescript
// Frontend - add to api.ts
api.interceptors.request.use(config => {
  console.log('Request:', config);
  return config;
});
```

### Performance Optimization

**Backend:**
- Implement caching with Redis
- Use background tasks for long-running operations
- Optimize database queries with indexes
- Use connection pooling

**Frontend:**
- Code splitting with React.lazy()
- Image optimization and lazy loading
- Implement virtual scrolling for large lists
- Use React.memo for expensive components

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the Repository**
```bash
git clone https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR.git
cd AI-VIDEO-GENERATOR
```

2. **Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make Your Changes**
- Write clean, documented code
- Follow existing code style
- Add tests for new features

4. **Commit Your Changes**
```bash
git add .
git commit -m "feat: add your feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

5. **Push and Create Pull Request**
```bash
git push origin feature/your-feature-name
```

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Maximum line length: 100 characters

**TypeScript (Frontend):**
- Use TypeScript strict mode
- Follow Airbnb style guide
- Use functional components
- Implement proper error handling

### Pull Request Process

1. Update README.md if needed
2. Update API documentation for new endpoints
3. Ensure all tests pass
4. Request review from maintainers
5. Address review feedback

### Reporting Issues

When reporting issues, include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, versions)
- Error messages and logs

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Manish Patidar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

### Project Links

- **GitHub Repository**: [AI-VIDEO-GENERATOR](https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR)
- **Issue Tracker**: [GitHub Issues](https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR/discussions)

### Maintainers

- **Manish Patidar** - [@ManishPatidar806](https://github.com/ManishPatidar806)

### Contributors

We appreciate all the contributors who have helped make this project better! 🙏

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/ManishPatidar806">
        <img src="https://github.com/ManishPatidar806.png" width="100px;" alt="Manish Patidar"/>
        <br />
        <sub><b>Manish Patidar</b></sub>
      </a>
      <br />
      💻 🎨 📖 🚧
    </td>
    <td align="center">
      <a href="https://github.com/sonali-parmar">
        <img src="https://github.com/sonali-parmar.png" width="100px;" alt="Sonali Parmar"/>
        <br />
        <sub><b>Sonali Parmar</b></sub>
      </a>
      <br />
      💻 🎨 📖
    </td>
  </tr>
</table>

**Emoji Legend:**
- 💻 Code
- 🎨 Design
- 📖 Documentation
- 🚧 Maintenance
- 🐛 Bug Reports
- 💡 Ideas & Feedback

### Community

- 🐛 Found a bug? [Report it](https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR/issues/new)
- 💡 Have an idea? [Share it](https://github.com/ManishPatidar806/AI-VIDEO-GENERATOR/discussions)
- 🤝 Want to contribute? Check [Contributing](#-contributing)

---

## 🙏 Acknowledgments

### Technologies & Services

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [LangChain](https://langchain.com/) - LLM orchestration
- [Google Generative AI](https://ai.google.dev/) - AI content generation
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing
- [Shadcn/UI](https://ui.shadcn.com/) - Component library
- [Radix UI](https://www.radix-ui.com/) - Headless components

### Inspiration

This project was inspired by the growing demand for automated video content creation and the potential of AI to democratize video production.

---

## 📊 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/ManishPatidar806/AI-VIDEO-GENERATOR)
![GitHub issues](https://img.shields.io/github/issues/ManishPatidar806/AI-VIDEO-GENERATOR)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ManishPatidar806/AI-VIDEO-GENERATOR)
![GitHub stars](https://img.shields.io/github/stars/ManishPatidar806/AI-VIDEO-GENERATOR?style=social)

### Roadmap

- [ ] Add support for multiple languages
- [ ] Implement video editing capabilities
- [ ] Add background music generation
- [ ] Support for custom voice models
- [ ] Mobile application (React Native)
- [ ] Advanced analytics dashboard
- [ ] Batch processing for multiple videos
- [ ] Integration with more AI models
- [ ] Custom branding options
- [ ] API rate limiting and quotas

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

Made with ❤️ by [Manish Patidar](https://github.com/ManishPatidar806)

[Back to Top](#-ai-video-generator)

</div>
