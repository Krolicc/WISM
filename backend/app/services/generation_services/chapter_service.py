

import uuid
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession 
from pydantic import BaseModel, Field

from app import crud, models, schemas
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

# ===================================================================
# 1. LLM-SPECIFIC PARSING SCHEMAS
# ===================================================================

class ChapterLLM(BaseModel):
    title: str = Field(description="The title of the chapter.")
    overview: str = Field(description="A detailed summary of the chapter.")
    description: str = Field(description="The full, detailed content of the chapter.")

class ChapterListLLM(BaseModel):
    chapters: List[ChapterLLM]

class ContentLLM(BaseModel):
    description: str = Field(description="The full, detailed content of the chapter.")

# ===================================================================
# 2. THE CHAPTER ORCHESTRATION SERVICE
# ===================================================================

class ChapterService(BaseOrchestrationService):
    def __init__(self):
        super().__init__()
        
    @property
    def model_name(self) -> str:
        return "chapter"

    @property
    def crud_manager(self) -> CRUDBase[models.Chapter, schemas.ChapterCreate, schemas.ChapterUpdate]:
        return crud.crud_chapter

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": {"schema": ChapterLLM, "name": "chapter"},
            "list": {"schema": ChapterListLLM, "name": "chapters"},
            "content": {"schema": ContentLLM, "name": "content"}
        }

    @property
    def parent_service(self) -> Optional["BaseOrchestrationService"]:
        from .arc_service import arc_service
        return arc_service

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        from .scene_service import scene_service
        return scene_service

    async def generate_chapters_from_prompt(
        self, db: AsyncSession, *, arc_id: uuid.UUID, prompt: str, num_chapters: int
    ) -> List[models.Chapter]:
        """Facade to generate chapter skeletons for a given arc."""
        return await super().generate_skeleton_from_prompt(
            db, parent_id=arc_id, prompt=prompt, count=num_chapters
        )

    async def rewrite_chapter_content(
        self, db: AsyncSession, *, chapter_id: uuid.UUID, prompt: Optional[str] = None
    ) -> models.Chapter:
        """Facade to write full content for a chapter."""
        return await super().rewrite_content(db, item_id=chapter_id, prompt=prompt)

    async def regenerate_chapter_skeleton_from_prompt(
        self, db: AsyncSession, *, chapter_id: uuid.UUID, prompt: str
    ) -> List[Any]:
        return await super().regenerate_skeleton_from_prompt(
            db, parent_id=arc_id, prompt=prompt
        )

    async def insert_chapters_and_generate_skeleton_from_prompt(
        self, db: AsyncSession, *,
        parent_id: uuid.UUID, prompt: str, count: int, insert_after_id: uuid.UUID
    ) -> models.Chapter:
        return await super().insert_item_and_generate_skeleton_from_prompt(
            db=db, parent_id=parent_id, prompt=prompt, count=count, previous_sibling_id=insert_after_id,
        )

# ===================================================================
# 3. SINGLETON INSTANCE
# ===================================================================

chapter_service = ChapterService()