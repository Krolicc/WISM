

import uuid
from typing import Optional, Type, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession 
from pydantic import BaseModel

from app import crud, schemas
from app.schemas.llm import LLMChapter, LLMChapterList
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

class ChapterService(BaseOrchestrationService):
    def __init__(self):
        super().__init__()
        
    @property
    def model_name(self) -> str:
        return "chapter"

    @property
    def crud_manager(self) -> CRUDBase:
        return crud.crud_chapter

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": LLMChapter,
            "list": {"schema": LLMChapterList, "name": "chapters"}
        }

    @property
    def create_schema(self) -> Type[BaseModel]:
        return schemas.ChapterCreate

    @property
    def update_schema(self) -> Type[BaseModel]:
        return schemas.ChapterUpdate

    @property
    def parent_id_field_name(self) -> str:
        return "story_id"

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        # Lazily import and instantiate to prevent circular dependencies
        from .scene_service import scene_service
        return scene_service

    async def _get_story_id(self, db: AsyncSession, parent_id: uuid.UUID) -> uuid.UUID:
        """For a chapter, the parent is the story, so the parent_id is the story_id."""
        return parent_id

chapter_service = ChapterService()