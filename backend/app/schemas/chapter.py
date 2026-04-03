
import uuid
from pydantic import BaseModel
from typing import List, Optional

class ChapterBase(BaseModel):
    title: str
    overview: Optional[str] = None
    description: Optional[str] = None

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(ChapterBase):
    title: Optional[str] = None

class ChapterRead(ChapterBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
