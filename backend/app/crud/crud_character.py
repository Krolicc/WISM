from .base import CRUDBase
from app.models import Character
from app.schemas import CharacterCreate, CharacterUpdate

class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):
    pass

character = CRUDCharacter(Character)
