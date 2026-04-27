
from enum import Enum

class GenerationTask(str, Enum):
    """Defines the available long-running tasks for the media service."""
    GENERATE_ENTITY_IMAGE = "generate_entity_image"
    GENERATE_FRAME_IMAGE = "generate_frame_image"
