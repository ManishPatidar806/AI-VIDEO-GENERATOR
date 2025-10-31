from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1.routers import auth_router
from app.api.v1.routers import transcript_generate_route
from app.api.v1.routers import transcript_regenerate_route
from contextlib import asynccontextmanager
import os

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (add cleanup code here if needed)

def create_app()->FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    @app.get("/")
    def root():
        return {"message": f"{settings.APP_NAME} is running!"}

    app.include_router(router=auth_router.router,prefix="/api/v1",tags=["auth"])
    app.include_router(router=transcript_generate_route.router, prefix="/api/v1/generate", 
    tags=["Generator"])
    app.include_router(router=transcript_regenerate_route.router, prefix="/api/v1/regenerate", 
    tags=["ReGenerate"])
    
    # Mount static file directories for serving generated images and videos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Mount generated_images directory
    generated_images_path = os.path.join(base_dir, "generated_images")
    if os.path.exists(generated_images_path):
        app.mount("/generated_images", StaticFiles(directory=generated_images_path), name="generated_images")
    
    # Mount nebius_scene_images directory
    nebius_images_path = os.path.join(base_dir, "nebius_scene_images")
    if os.path.exists(nebius_images_path):
        app.mount("/nebius_scene_images", StaticFiles(directory=nebius_images_path), name="nebius_scene_images")
    
    # Mount generated_videos directory
    generated_videos_path = os.path.join(base_dir, "generated_videos")
    if os.path.exists(generated_videos_path):
        app.mount("/generated_videos", StaticFiles(directory=generated_videos_path), name="generated_videos")
    
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=["http://localhost:8080"],  # your frontend URL
        allow_credentials=True,  # required for cookies
        )

    return app

app = create_app()