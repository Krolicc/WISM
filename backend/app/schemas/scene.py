
import uuid
from pydantic import BaseModel
from typing import List, Optional

class SceneBase(BaseModel):
    title: str
    overview: Optional[str] = None
    description: Optional[str] = None

class SceneCreate(SceneBase):
    pass

class SceneUpdate(SceneBase):
    title: Optional[str] = None

class SceneRead(SceneBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
