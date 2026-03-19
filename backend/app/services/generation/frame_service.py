
import uuid
from typing import Optional, Type, Dict, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.schemas.llm import LLMFrame, LLMFrameList
from app.crud.base import CRUDBase
from .base_orchestration import BaseOrchestrationService

class FrameService(BaseOrchestrationService):
    def __init__(self):
        super().__init__()
        
    @property
    def model_name(self) -> str:
        return "frame"

    @property
    def crud_manager(self) -> CRUDBase:
        return crud.crud_frame

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": LLMFrame,
            "list": {"schema": LLMFrameList, "name": "frames"}
        }

    @property
    def create_schema(self) -> Type[BaseModel]:
        return schemas.FrameCreate

    @property
    def update_schema(self) -> Type[BaseModel]:
        return schemas.FrameUpdate

    @property
    def parent_id_field_name(self) -> str:
        return "scene_id"

    @property
    def child_service(self) -> Optional[BaseOrchestrationService]:
        # Frames are the lowest level, they have no children
        return None


frame_service = FrameService()
