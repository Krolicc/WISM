import uuid

from sqlalchemy import Column, String, Text, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class Frame(Base):
    """
    Stores the 'heavy' content for a Frame node.
    """
    __tablename__ = 'frames'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    overview = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    detailed_prompt = Column(JSONB, nullable=False, server_default='{}', default=dict)
    use_detailed_prompt = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
