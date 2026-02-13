from pydantic import BaseModel
import uuid
from typing import Optional


class PanelBase(BaseModel):
    panel_number: int
    description: Optional[str] = None
    image_url: Optional[str] = None


class PanelCreate(PanelBase):
    scene_id: uuid.UUID


class PanelUpdate(PanelBase):
    pass


class PanelRead(PanelBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
