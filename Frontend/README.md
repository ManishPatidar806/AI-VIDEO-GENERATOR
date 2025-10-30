# AI Video Creator - Frontend

Production-ready Chrome Extension UI for automated AI-powered video creation from YouTube content.

## Features

✅ Full authentication system with JWT
✅ Complete pipeline integration with backend API
✅ Step-by-step workflow (Transcript → Story → Images → Video)
✅ One-click complete pipeline automation
✅ Project management with regeneration capabilities
✅ Modern glassmorphic design system

## Quick Start

```sh
# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

## Backend Integration

All 15+ backend endpoints integrated:
- Auth (signup, login)
- Transcript generation
- Story/script generation with regeneration
- AI image generation with batch operations
- Video generation and assembly
- Voiceover generation
- Final video compilation
- Complete pipeline automation

## Tech Stack

- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- Axios for API calls
- React Router v6
- TanStack Query
- Vite

## Project Structure

```
src/
├── components/     # UI components
├── contexts/       # AuthContext
├── lib/           # API client
├── pages/         # Route pages
└── App.tsx        # Root with routing
```

## Deployment

Simply open [Lovable](https://lovable.dev/projects/2794787b-6d71-4daa-9fc8-4a9de5142e00) and click Share → Publish.
