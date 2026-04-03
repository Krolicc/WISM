
from pydantic import BaseModel
import uuid
from typing import List, Optional

from .enums import GenerationStage

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(StoryBase):
    title: Optional[str] = None

class StoryRead(StoryBase):
    id: uuid.UUID

    class Config:
        from_attributes = True