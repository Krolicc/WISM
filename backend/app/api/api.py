from fastapi import APIRouter

from app.api.endpoints import character, panel, scene, story

api_router = APIRouter()

api_router.include_router(story.router, prefix="/stories", tags=["stories"])
api_router.include_router(character.router, prefix="/characters", tags=["characters"])
api_router.include_router(scene.router, prefix="/scenes", tags=["scenes"])
api_router.include_router(panel.router, prefix="/panels", tags=["panels"])
