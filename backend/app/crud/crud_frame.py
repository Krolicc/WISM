
from .base import CRUDBase
from app.models import Frame
from app.schemas import FrameCreate, FrameUpdate

class CRUDFrame(CRUDBase[Frame, FrameCreate, FrameUpdate]):
    pass

crud_frame = CRUDFrame(Frame)
