
import enum

class GenerationStatus(str, enum.Enum):
    """Enum for the status of a generation task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
