from .base import CRUDBase
from app.models import Panel
from app.schemas import PanelCreate, PanelUpdate

class CRUDPanel(CRUDBase[Panel, PanelCreate, PanelUpdate]):
    pass

panel = CRUDPanel(Panel)
