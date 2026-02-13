from pydantic import BaseModel
import uuid
from typing import Optional


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None


class CharacterCreate(CharacterBase):
    story_id: uuid.UUID


class CharacterUpdate(CharacterBase):
    pass


class CharacterRead(CharacterBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
