import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Base schema with fields common to all Frame variants
class FrameBase(BaseModel):
    # Simple text description for the frame
    common_description: Optional[str] = None
    
    # Detailed JSON prompt for image generation, defaults to an empty dict
    detailed_prompt: Dict[str, Any] = Field(default_factory=dict)
    
    # Flag to select which description to use for generation
    use_detailed_prompt: bool = False
    
    # URL of the generated image
    image_url: Optional[str] = None
    
    # Order of the frame within the scene
    order: int

# Schema for creating a frame (requires scene_id)
class FrameCreate(FrameBase):
    scene_id: uuid.UUID

# Schema for updating a frame (all fields are optional)
class FrameUpdate(FrameBase):
    detailed_prompt: Optional[Dict[str, Any]] = None
    use_detailed_prompt: Optional[bool] = None
    order: Optional[int] = None

# Schema for reading/representing a frame from the database
class FrameRead(FrameBase):
    id: uuid.UUID
    scene_id: uuid.UUID

    class Config:
        from_attributes = True
