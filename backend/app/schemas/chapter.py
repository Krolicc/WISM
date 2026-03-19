
from pydantic import BaseModel
import uuid
from typing import List, Optional

class ChapterBase(BaseModel):
    title: str
    description: Optional[str] = None

class ChapterCreate(ChapterBase):
    story_id: uuid.UUID
    order: int

class ChapterUpdate(ChapterBase):
    title: Optional[str] = None
    order: Optional[int] = None

class ChapterRead(ChapterBase):
    id: uuid.UUID
    order: int
    scenes: List["SceneRead"] = []

    class Config:
        from_attributes = True

from .scene import SceneRead

ChapterRead.model_rebuild()
