import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class FrameBase(BaseModel):
    overview: str
    description: Optional[str] = None
    detailed_prompt: Dict[str, Any] = Field(default_factory=dict)
    use_detailed_prompt: bool = False

class FrameCreate(FrameBase):
    pass

class FrameUpdate(FrameBase):
    overview: Optional[str] = None
    detailed_prompt: Optional[Dict[str, Any]] = None
    use_detailed_prompt: Optional[bool] = None

class FrameRead(FrameBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
