
import uuid
from sqlalchemy import Column, DateTime, Enum, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from app.enums.generation_status import GenerationStatus

Base = declarative_base()

class Generation(Base):
    __tablename__ = "generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_data = Column(JSON, nullable=False)
    status = Column(Enum(GenerationStatus), nullable=False, default=GenerationStatus.PENDING)
    generated_at = Column(DateTime, server_default=func.now())
    result_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    storage_key = Column(String, nullable=True)
    frame_id = Column(UUID(as_uuid=True), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
