from pydantic import BaseModel
from typing import List, Optional, Literal, Union
import uuid

# class GenerateAction(BaseModel):
#     id: Optional[uuid.UUID] = None
#     idea: Optional[str] = None
#     count: Optional[int] = None
#     obj_in: Optional[BaseModel] = None
#     parent_id: Optional[uuid.UUID] = None
#     before_id: Optional[uuid.UUID] = None
#     after_id: Optional[uuid.UUID] = None

class GenerateAction(BaseModel):
    idea: str = None
    count: int
    parent_id: uuid.UUID
    before_id: Optional[uuid.UUID] = None
    after_id: Optional[uuid.UUID] = None

class RegenAction(BaseModel):
    id: uuid.UUID
    idea: str
    count: Optional[int] = None

class DeleteAction(BaseModel):
    id: uuid.UUID

class BaseActions(BaseModel):
    level: Literal['chapter', 'scene', 'frame']
    action_type: Literal['generate', 'regenerate', 'delete']

class CRUDActions(BaseActions):
    params: DeleteAction

class GenerateActions(BaseActions):
    params: Union[RegenAction, GenerateAction]

class OrchestrationActions(BaseModel):
    crud: List[CRUDActions]
    generate: List[GenerateActions]

    class Config:
        from_attributes = True

class OrchestrationError(Exception):
    """Custom exception for orchestration errors."""
    pass