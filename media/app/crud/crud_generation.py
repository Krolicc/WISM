
from app.crud.base import CRUDBase
from app.models.generation import Generation
from app.schemas.generation import GenerationCreate, GenerationUpdate, GenerationRead

class CRUDGeneration(CRUDBase[Generation, GenerationCreate, GenerationUpdate, GenerationRead]):
    pass

crud_generation = CRUDGeneration(Generation, GenerationRead)
