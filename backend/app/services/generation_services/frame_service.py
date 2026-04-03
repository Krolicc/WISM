
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

class FrameLLM(BaseModel):
    overview: str = Field(description="The title of the frame.")

class FrameListLLM(BaseModel):
    frames: List[FrameLLM]

class ContentLLM(BaseModel):
    description: str = Field(description="The full, detailed content of the frame.")

# ===================================================================
# 2. THE FRAME ORCHESTRATION SERVICE
# ===================================================================

class FrameService(BaseOrchestrationService):
    
    # --- Abstract Property Implementations ---
    
    @property
    def model_name(self) -> str:
        return "frame"

    @property
    def crud_manager(self) -> CRUDBase[models.Frame, schemas.FrameCreate, schemas.FrameUpdate]:
        return crud.crud_frame

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": {"schema": FrameLLM, "name": "frame"},
            "list": {"schema": FrameListLLM, "name": "frames"},
            "content": {"schema": ContentLLM, "name": "content"}
        }

    @property
    def parent_service(self) -> Optional["BaseOrchestrationService"]:
        from .scene_service import scene_service
        return scene_service

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        return None

    # --- Public-Facing Facade Methods ---

    async def generate_frames_from_prompt(
        self, db: AsyncSession, *, scene_id: uuid.UUID, prompt: str, num_frames: int
    ) -> List[models.Frame]:
        return await super().generate_skeleton_from_prompt(
            db, parent_id=scene_id, prompt=prompt, count=num_frames
        )

    async def rewrite_frame_content(
        self, db: AsyncSession, *, frame_id: uuid.UUID, prompt: Optional[str] = None
    ) -> models.Frame:
        return await super().rewrite_content(db, item_id=frame_id, prompt=prompt)

        
    # --- Special-Purpose Methods ---

    async def generate_image(self, db: AsyncSession, *, frame_id: uuid.UUID, prompt: str) -> models.Frame:
        """Generates an image for a frame and updates its record."""
        frame = await self.crud_manager.get(db, id=frame_id)
        if not frame:
            raise ValueError(f"Frame with id {frame_id} not found.")
        
        # In a real implementation, this would call an image generation API.
        # For now, we simulate this by creating a placeholder URL.
        print(f"Image generation called for frame {frame_id} with style prompt: {prompt}")
        image_url = f"https://placeholder.art/image_for_{frame_id}.jpg"
        
        frame_update = schemas.FrameUpdate(image_url=image_url)
        updated_frame = await self.crud_manager.update(db, db_obj=frame, obj_in=frame_update)
        return updated_frame


# ===================================================================
# 3. SINGLETON INSTANCE
# ===================================================================

frame_service = FrameService()
