
import abc
from typing import Optional, Type, Dict, Any

from pydantic import BaseModel

from app import crud, schemas
from app.schemas.llm import LLMStory
from app.crud.base import CRUDBase
from app.schemas import StoryCreate, StoryUpdate
from .base_orchestration import BaseOrchestrationService


# Note: StoryService is a special case. It doesn't have LLM-based content
# generation for itself, but it acts as the root of the hierarchy.
# Its primary role is to link to its children (chapters).

class StoryService(BaseOrchestrationService):
    def __init__(self):
        super().__init__()
        
    @property
    def model_name(self) -> str:
        return "story"

    @property
    def crud_manager(self) -> CRUDBase:
        return crud.crud_story

    @property
    def llm_schemas(self) -> Dict[str, Any]:
        return {
            "single": LLMStory,
            "list": {"schema": None, "name": "stories"}
        }

    @property
    def create_schema(self) -> Type[BaseModel]:
        return StoryCreate

    @property
    def update_schema(self) -> Type[BaseModel]:
        return StoryUpdate

    @property
    def parent_id_field_name(self) -> str:
        # Story is the root, so it has no parent in the content hierarchy.
        # The field linking to a user is a different concern.
        return ""

    @property
    def child_service(self) -> Optional["BaseOrchestrationService"]:
        # Lazily import and instantiate to prevent circular dependencies
        from .chapter_service import chapter_service
        return chapter_service


story_service = StoryService()
