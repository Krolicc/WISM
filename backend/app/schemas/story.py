from pydantic import BaseModel
import uuid
from typing import List, Optional

# Note: We use string forward references for recursive models
# e.g., 'CharacterRead' instead of CharacterRead

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None


class StoryCreate(StoryBase):
    pass


class StoryUpdate(StoryBase):
    pass


class StoryRead(StoryBase):
    id: uuid.UUID
    characters: List["CharacterRead"] = []
    scenes: List["SceneRead"] = []

    class Config:
        from_attributes = True

# Import dependent schemas and update forward references
from .character import CharacterRead
from .scene import SceneRead

StoryRead.model_rebuild()
