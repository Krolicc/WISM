
from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.entity import EntityDescriptionFragment
from app.schemas.entity import EntityDescriptionFragmentCreate, EntityDescriptionFragmentUpdate

class CRUDEntityFragment(CRUDBase[EntityDescriptionFragment, EntityDescriptionFragmentCreate, EntityDescriptionFragmentUpdate]):
    """
    CRUD operations for EntityDescriptionFragment.
    """
    async def create_multi(
        self, db: AsyncSession, *, objs_in: List[EntityDescriptionFragmentCreate]
    ) -> List[EntityDescriptionFragment]:
        """Create multiple description fragments in a single transaction."""
        db_objs = [self.model(**obj.dict()) for obj in objs_in]
        db.add_all(db_objs)
        # Note: We rely on the calling function to commit the session.
        return db_objs

    async def get_multi_by_entity(
        self, db: AsyncSession, *, entity_id: uuid.UUID
    ) -> List[EntityDescriptionFragment]:
        """Retrieve all fragments associated with a specific entity."""
        result = await db.execute(
            select(self.model).where(self.model.entity_id == entity_id)
        )
        return result.scalars().all()

# Create a singleton instance of the CRUD class
crud_fragment = CRUDEntityFragment(EntityDescriptionFragment)
