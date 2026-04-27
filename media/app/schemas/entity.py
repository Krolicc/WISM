
import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict 

from .enums import EntityType
from .entity_description_fragment import EntityDescriptionFragmentBase


class EntityBase(BaseModel):
    """Base schema for an entity."""
    canonical_name: str
    type: EntityType
    aliases: Dict[str, Any] = Field(default_factory=dict)
    detailed_prompt: Dict[str, Any] = Field(default_factory=dict)
    use_detailed_prompt: bool = False

class EntityCreate(EntityBase):
    """Schema for creating a new entity. Can be created with a description."""
    description: Optional[str] = None

class EntityUpdate(EntityBase):
    """Schema for updating an entity. All fields are optional."""
    canonical_name: Optional[str] = None
    type: Optional[EntityType] = None
    description: Optional[str] = None
    is_description_stale: Optional[bool] = None
    detailed_prompt: Dict[str, Any] = Field(default_factory=dict)
    use_detailed_prompt: bool = False

class EntityRead(EntityBase):
    """The full schema for an entity, as returned from the API."""
    id: uuid.UUID
    is_description_stale: bool
    description: Optional[str] = None
    
    # The associated fragments are included in the full entity representation
    description_fragments: List[EntityDescriptionFragmentBase] = []

    model_config = ConfigDict(from_attributes=True)
