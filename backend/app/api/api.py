from fastapi import APIRouter

from .endpoints import story, orchestration, vector, web_socket, graph

api_router = APIRouter()

api_router.include_router(story.router, prefix="/stories", tags=["stories"])
# api_router.include_router(character.router, prefix="/characters", tags=["characters"])
api_router.include_router(orchestration.router, prefix="/stories", tags=["orchestration"])
api_router.include_router(vector.router, prefix="/vectors", tags=["vectors"])
api_router.include_router(web_socket.router, prefix="/web_socket", tags=["web_socket"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
