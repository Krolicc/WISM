
import uuid
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

# --- Description Fragment Schemas ---

class EntityDescriptionFragmentBase(BaseModel):
    """Base schema for a fragment, containing the core data."""
    fragment_text: str = Field(..., description="The atomic piece of information about the entity.")
    source_node_id: int = Field(..., description="The ID of the source node (e.g., Scene) from the Neo4j graph.")
    value_score: int = Field(default=5, ge=1, le=10, description="The assessed importance of this fragment (1-10).")

class EntityDescriptionFragmentCreate(EntityDescriptionFragmentBase):
    """Schema used for creating a new fragment. Requires linking to an entity."""
    entity_id: uuid.UUID

class EntityDescriptionFragmentUpdate(BaseModel):
    """Schema for updating an existing fragment (e.g., reassessing its value)."""
    fragment_text: Optional[str] = None
    value_score: Optional[int] = None

class EntityDescriptionFragmentRead(EntityDescriptionFragmentBase):
    """The full schema for a fragment, as returned from the API."""
    id: uuid.UUID
    entity_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)