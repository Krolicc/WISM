
from .base import CRUDBase
from app.models import Scene
from app.schemas import SceneCreate, SceneUpdate


class CRUDScene(CRUDBase[Scene, SceneCreate, SceneUpdate]):
    pass

crud_scene = CRUDScene(Scene)
