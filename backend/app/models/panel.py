import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Panel(Base):
    __tablename__ = "panels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    panel_number = Column(Integer, nullable=False)
    image_url = Column(String)  # URL to the generated image
    description = Column(Text)  # Description/prompt for the image
    scene_id = Column(UUID(as_uuid=True), ForeignKey("scenes.id"), nullable=False)

    # Relationship
    scene = relationship("Scene", back_populates="panels")
