
from .base import CRUDBase
from app.models import Arc
from app.schemas import ArcCreate, ArcUpdate

class CRUDArc(CRUDBase[Arc, ArcCreate, ArcUpdate]):
    pass

crud_arc = CRUDArc(Arc)
