
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from app.enums.generation_status import GenerationStatus
from datetime import datetime

class GenerationBase(BaseModel):
    prompt_data: dict
    status: GenerationStatus = GenerationStatus.PENDING
    frame_id: Optional[uuid.UUID] = None
    entity_id: Optional[uuid.UUID] = None

class GenerationCreate(GenerationBase):
    pass

class GenerationUpdate(BaseModel):
    status: Optional[GenerationStatus] = None
    result_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    storage_key: Optional[str] = None

class GenerationRead(GenerationBase):
    id: uuid.UUID
    generated_at: datetime
    result_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    storage_key: Optional[str] = None

    class Config:
        orm_mode = True
