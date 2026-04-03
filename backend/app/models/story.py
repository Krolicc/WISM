import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Story(Base):
    """
    Stores the 'heavy' content for a Story node.
    The primary key (story_id) is synchronized with the 'id' property of the corresponding :Story node in Neo4j.
    """
    __tablename__ = 'stories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
