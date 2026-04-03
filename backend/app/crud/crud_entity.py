
from .base import CRUDBase
from app.models import Entity
from app.schemas.entity import EntityCreate, EntityUpdate

class CRUDEntity(CRUDBase[Entity, EntityCreate, EntityUpdate]):
    pass

crud_entity = CRUDEntity(Entity)
