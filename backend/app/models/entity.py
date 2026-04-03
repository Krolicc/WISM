import enum
import uuid

from sqlalchemy import Column, String, Text, DateTime, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base

class EntityType(enum.Enum):
    CHARACTER = "character"
    LOCATION = "location"

class Entity(Base):
    """
    Stores the 'heavy' content for an Entity node.
    """
    __tablename__ = 'entities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    canonical_name = Column(String, index=True, nullable=False)
    type = Column(SAEnum(EntityType), index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_description_stale = Column(Boolean, default=True, nullable=False)
    aliases = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    description_fragments = relationship("EntityDescriptionFragment", back_populates="entity", cascade="all, delete-orphan")
