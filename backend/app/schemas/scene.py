from pydantic import BaseModel
import uuid
from typing import List, Optional

# Note: We use a string forward reference for the recursive model 'PanelRead'

class SceneBase(BaseModel):
    name: str


class SceneCreate(SceneBase):
    story_id: uuid.UUID


class SceneUpdate(SceneBase):
    pass


class SceneRead(SceneBase):
    id: uuid.UUID
    panels: List["PanelRead"] = []

    class Config:
        from_attributes = True

# Import the dependent schema and update the forward reference
from .panel import PanelRead

SceneRead.model_rebuild()
