
import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

class FrameBase(BaseModel):
    title: str
    description: str
    detailed_prompt: Dict[str, Any] = Field(default_factory=dict)
    use_detailed_prompt: bool = False

class FrameCreate(FrameBase):
    pass

class FrameUpdate(FrameBase):
    title: Optional[str] = None
    description: Optional[str] = None
    detailed_prompt: Optional[Dict[str, Any]] = None
    use_detailed_prompt: Optional[bool] = None

class FrameRead(FrameBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
