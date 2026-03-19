import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base

class Frame(Base):
    __tablename__ = "frames"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    scene_id = Column(UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    common_description = Column(Text, nullable=True)
    detailed_prompt = Column(JSONB, nullable=False, server_default='{}', default=dict)
    use_detailed_prompt = Column(Boolean, default=False, nullable=False)
    image_url = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    scene = relationship("Scene", back_populates="frames")
