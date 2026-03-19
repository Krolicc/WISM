
import uuid
from typing import Optional, Type, Dict, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.schemas.llm import LLMScenePoint, LLMScenePointList
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

class SceneService(BaseOrchestrationService):
    def __init__(self):
        super().__init__()

    @property
    def model_name(self) -> str:
        return "scene"

    @property
    def crud_manager(self) -> CRUDBase:
        return crud.crud_scene

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": LLMScenePoint,
            "list": {"schema": LLMScenePointList, "name": "scenes"}
        }

    @property
    def create_schema(self) -> Type[BaseModel]:
        return schemas.SceneCreate

    @property
    def update_schema(self) -> Type[BaseModel]:
        return schemas.SceneUpdate

    @property
    def parent_id_field_name(self) -> str:
        return "chapter_id"

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        # Lazily import and instantiate to prevent circular dependencies
        from .frame_service import frame_service
        return frame_service

    async def _get_story_id(self, db: AsyncSession, parent_id: uuid.UUID) -> uuid.UUID:
        """Retrieves the story ID from the parent chapter."""
        chapter = await crud.crud_chapter.get(db, id=parent_id)
        if not chapter:
            raise ValueError("Chapter not found")
        return chapter.story_id

scene_service = SceneService()
