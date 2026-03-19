
from pydantic import BaseModel
import uuid
from typing import List, Optional

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(StoryBase):
    pass

class StoryRead(StoryBase):
    id: uuid.UUID
    # characters: List["CharacterRead"] = []
    chapters: List["ChapterRead"] = []

    class Config:
        from_attributes = True

# from .character import CharacterRead
from .chapter import ChapterRead

StoryRead.model_rebuild()
