import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="story", cascade="all, delete-orphan")
