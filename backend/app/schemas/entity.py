
import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import EntityType
from .entity_description_fragment import EntityDescriptionFragment


class EntityBase(BaseModel):
    """Base schema for an entity."""
    canonical_name: str
    type: EntityType
    aliases: Optional[str] = None

class EntityCreate(EntityBase):
    """Schema for creating a new entity. Can be created with a description."""
    description: Optional[str] = None

class EntityUpdate(BaseModel):
    """Schema for updating an entity. All fields are optional."""
    canonical_name: Optional[str] = None
    type: Optional[EntityType] = None
    aliases: Optional[str] = None
    description: Optional[str] = None
    is_description_stale: Optional[bool] = None

class EntityRead(EntityBase):
    """The full schema for an entity, as returned from the API."""
    id: uuid.UUID
    is_description_stale: bool
    description: Optional[str] = None
    
    # The associated fragments are included in the full entity representation
    description_fragments: List[EntityDescriptionFragment] = []

    class Config:
        from_attributes = True
