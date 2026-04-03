
import uuid
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

# ===================================================================
# 1. LLM-SPECIFIC PARSING SCHEMAS
# ===================================================================

class SceneLLM(BaseModel):
    title: str = Field(description="The title of the scene.")
    overview: str = Field(description="A detailed summary of the scene.")
    description: str = Field(description="The full, detailed content of the scene.")

class SceneListLLM(BaseModel):
    scenes: List[SceneLLM]

class ContentLLM(BaseModel):
    description: str = Field(description="The full, detailed content of the scene.")

# ===================================================================
# 2. THE SCENE ORCHESTRATION SERVICE
# ===================================================================

class SceneService(BaseOrchestrationService):
    
    # --- Abstract Property Implementations ---
    
    @property
    def model_name(self) -> str:
        return "scene"

    @property
    def crud_manager(self) -> CRUDBase[models.Scene, schemas.SceneCreate, schemas.SceneUpdate]:
        return crud.crud_scene

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": {"schema": SceneLLM, "name": "scene"},
            "list": {"schema": SceneListLLM, "name": "scenes"},
            "content": {"schema": ContentLLM, "name": "content"}
        }

    @property
    def parent_service(self) -> Optional["BaseOrchestrationService"]:
        from .chapter_service import chapter_service
        return chapter_service

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        from .frame_service import frame_service
        return frame_service

    # --- Public-Facing Facade Methods ---

    async def generate_scenes_from_prompt(
        self, db: AsyncSession, *, chapter_id: uuid.UUID, prompt: str, num_scenes: int
    ) -> List[models.Scene]:
        """Facade to generate scene skeletons for a given chapter."""
        return await super().generate_skeleton_from_prompt(
            db, parent_id=chapter_id, prompt=prompt, count=num_scenes
        )

    async def rewrite_scene_content(
        self, db: AsyncSession, *, scene_id: uuid.UUID, prompt: Optional[str] = None
    ) -> models.Scene:
        """Facade to write full content for a scene."""
        return await super().rewrite_content(db, item_id=scene_id, prompt=prompt)

    async def regenerate_chapter_skeleton_from_prompt(
        self, db: AsyncSession, *, scene_id: uuid.UUID, prompt: str
    ) -> List[Any]:
        return await super().regenerate_skeleton_from_prompt(
            db, parent_id=arc_id, prompt=prompt
        )

    async def insert_chapters_and_generate_skeleton_from_prompt(
        self, db: AsyncSession, *,
        parent_id: uuid.UUID, prompt: str, count: int, insert_after_id: uuid.UUID
    ) -> models.Scene:
        return await super().insert_item_and_generate_skeleton_from_prompt(
            db=db, parent_id=parent_id, prompt=prompt, count=count, previous_sibling_id=insert_after_id,
        )

# ===================================================================
# 3. SINGLETON INSTANCE
# ===================================================================

scene_service = SceneService()
