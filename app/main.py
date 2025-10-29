from fastapi import FastAPI
from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1.routers import auth as auth_router


from fastapi.middleware.cors import CORSMiddleware

def create_app()->FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    @app.on_event('startup')
    def on_startup():
        init_db()

    @app.get("/")
    def root():
        return {"message": f"{settings.APP_NAME} is running!"}

    app.include_router(router=auth_router.router,prefix="/api")




#    Sample router include
    # app.include_router(router=route_transcript.router,prefix="/api/v1/transcript",tags=["transcript"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
        )

    return app

app = create_app()