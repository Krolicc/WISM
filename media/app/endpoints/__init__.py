from fastapi import APIRouter

from . import orchestration, crdt, auth

api_router = APIRouter()

api_router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])
api_router.include_router(crdt.router, prefix="/crdt", tags=["crdt"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
