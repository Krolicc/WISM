import enum
import uuid

from sqlalchemy import Column, String, Text, Boolean, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base

class EntityType(enum.Enum):
    CHARACTER = "character"
    LOCATION = "location"

class Entity(Base):
    """
    Stores the 'heavy' content for an Entity node.
    """
    __tablename__ = 'entities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(SAEnum(EntityType), index=True, nullable=False)
    canonical_name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    detailed_prompt = Column(JSONB, nullable=False, server_default='{}', default=dict)
    use_detailed_prompt = Column(Boolean, default=False, nullable=False)
    is_description_stale = Column(Boolean, default=True, nullable=False)
    aliases = Column(JSONB, nullable=False, server_default='{}', default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())