import uuid

from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Arc(Base):
    """
    Stores the 'heavy' content for an Arc node.
    The primary key (arc_id) is synchronized with the 'id' property of the corresponding :Arc node in Neo4j.
    """
    __tablename__ = 'arcs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    overview = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
