
import uuid
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

# ===================================================================
# 1. LLM-SPECIFIC PARSING SCHEMAS
# These models define the expected structure of the LLM's output.
# ===================================================================

class ArcLLM(BaseModel):
    title: str = Field(description="The title of the story arc.")
    overview: str = Field(description="A detailed summary of the story arc.")
    description: str = Field(description="The full, detailed content of the story arc.")

class ArcListLLM(BaseModel):
    arcs: List[ArcLLM]

class ContentLLM(BaseModel):
    description: str = Field(description="The full, detailed content of the story arc.")

# ===================================================================
# 2. THE ARC ORCHESTRATION SERVICE
# Inherits from the base service and implements the abstract methods.
# ===================================================================

class ArcService(BaseOrchestrationService):
    
    # --- Abstract Property Implementations ---
    
    @property
    def model_name(self) -> str:
        return "arc"

    @property
    def crud_manager(self) -> CRUDBase[models.Arc, schemas.ArcCreate, schemas.ArcUpdate]:
        return crud.crud_arc

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "item": {"schema": ArcLLM, "name": "arc"},
            "list": {"schema": ArcListLLM, "name": "arcs"},
            "content": {"schema": ContentLLM, "name": "content"}
        }

    @property
    def parent_service(self) -> Optional["BaseOrchestrationService"]:
        return None

    @property
    def child_service(self) -> Optional["BaseOrchestrationService"]:
        from .chapter_service import chapter_service
        return chapter_service

    # --- Public-Facing Facade Methods (called by Celery tasks) ---

    async def generate_arcs_from_prompt(
        self, db: AsyncSession, *, story_id: uuid.UUID, prompt: str, num_arcs: int
    ) -> List[models.Arc]:
        """Facade method to generate arc skeletons. Explicitly calls base service logic."""
        return await super().generate_skeleton_from_prompt(
            db, parent_id=story_id, prompt=prompt, count=num_arcs
        )

    async def rewrite_arc_content(
        self, db: AsyncSession, *, arc_id: uuid.UUID, prompt: Optional[str] = None
    ) -> models.Arc:
        """Facade method to write full content for an arc. Explicitly calls base service logic."""
        return await super().rewrite_content(db, item_id=arc_id, prompt=prompt)

    async def regenerate_chapter_skeleton_from_prompt(
        self, db: AsyncSession, *, arc_id: uuid.UUID, prompt: str
    ) -> List[Any]:
        return await super().regenerate_skeleton_from_prompt(
            db, parent_id=arc_id, prompt=prompt
        )

    async def insert_chapters_and_generate_skeleton_from_prompt(
        self, db: AsyncSession, *,
        parent_id: uuid.UUID, prompt: str, count: int, insert_after_id: uuid.UUID
    ) -> models.Arc:
        return await super().insert_item_and_generate_skeleton_from_prompt(
            db=db, parent_id=parent_id, prompt=prompt, count=count, previous_sibling_id=insert_after_id,
        )

# ===================================================================
# 3. SINGLETON INSTANCE
# ===================================================================

arc_service = ArcService()
