
import uuid
from sqlalchemy import delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base import CRUDBase
from .mixins import OrderableCRUDMixin # Import the mixin
from app.models import Frame
from app.schemas import FrameCreate, FrameUpdate

class CRUDFrame(CRUDBase[Frame, FrameCreate, FrameUpdate], OrderableCRUDMixin):

    # --- Methods using the mixin --- #

    async def get_max_order_for_scene(self, db: AsyncSession, scene_id: uuid.UUID) -> int:
        return await self.get_max_order(db, parent_id_field_name="scene_id", parent_id=scene_id)

    async def get_min_order_for_scene(self, db: AsyncSession, scene_id: uuid.UUID) -> int:
        return await self.get_min_order(db, parent_id_field_name="scene_id", parent_id=scene_id)

    async def shift_orders_after(self, db: AsyncSession, *, scene_id: uuid.UUID, after_order: int, shift_value: int) -> None:
        return await super().shift_orders_after(
            db, parent_id_field_name="scene_id", parent_id=scene_id, after_order=after_order, shift_value=shift_value
        )

    # --- Other specific methods --- #

    async def delete_by_scene_id(self, db: AsyncSession, parent_id: uuid.UUID) -> None:
        """Deletes all frames associated with a given scene_id."""
        statement = delete(self.model).where(self.model.scene_id == parent_id)
        await db.execute(statement)
        await db.commit()


crud_frame = CRUDFrame(Frame)
