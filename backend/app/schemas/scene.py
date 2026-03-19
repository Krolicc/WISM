
from pydantic import BaseModel
import uuid
from typing import List, Optional

class SceneBase(BaseModel):
    title: str
    description: Optional[str] = None

class SceneCreate(SceneBase):
    chapter_id: uuid.UUID
    order: int

class SceneUpdate(SceneBase):
    title: Optional[str] = None
    order: Optional[int] = None

class SceneRead(SceneBase):
    id: uuid.UUID
    order: int
    frames: List["FrameRead"] = []

    class Config:
        from_attributes = True

from .frame import FrameRead

SceneRead.model_rebuild()
