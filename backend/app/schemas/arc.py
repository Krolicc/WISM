
import uuid
from pydantic import BaseModel
from typing import Optional, List

class ArcBase(BaseModel):
    title: str
    overview: Optional[str] = None
    description: Optional[str] = None

class ArcCreate(ArcBase):
    pass

class ArcUpdate(BaseModel):
    title: Optional[str] = None

class ArcRead(ArcBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True