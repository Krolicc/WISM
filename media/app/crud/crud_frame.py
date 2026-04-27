
from .base import CRUDBase
from app.models import Frame
from app.schemas import FrameCreate, FrameUpdate, FrameRead

class CRUDFrame(CRUDBase[Frame, FrameCreate, FrameUpdate, FrameRead]):
    pass

crud_frame = CRUDFrame(Frame, FrameRead)
