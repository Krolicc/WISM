
from .base import CRUDBase
from app.models import Entity
from app.schemas.entity import EntityCreate, EntityUpdate, EntityRead

class CRUDEntity(CRUDBase[Entity, EntityCreate, EntityUpdate, EntityRead]):
    pass

crud_entity = CRUDEntity(Entity, EntityRead)
