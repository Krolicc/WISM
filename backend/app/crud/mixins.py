
import uuid
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class OrderableCRUDMixin:
    """
    A mixin for CRUD classes that adds reusable logic for models with an 'order' field.
    """

    async def get_max_order(
        self, db: AsyncSession, *, parent_id_field_name: str, parent_id: uuid.UUID
    ) -> int:
        """
        Gets the maximum 'order' value for a given parent.
        
        :param parent_id_field_name: The name of the foreign key field on the model (e.g., 'story_id').
        :param parent_id: The ID of the parent entity.
        """
        parent_field = getattr(self.model, parent_id_field_name)
        statement = select(func.max(self.model.order)).where(parent_field == parent_id)
        result = await db.execute(statement)
        max_order = result.scalar_one_or_none()
        return max_order if max_order is not None else 0

    async def get_min_order(
        self, db: AsyncSession, *, parent_id_field_name: str, parent_id: uuid.UUID
    ) -> int:
        """
        Gets the minimum 'order' value for a given parent.

        :param parent_id_field_name: The name of the foreign key field on the model (e.g., 'story_id').
        :param parent_id: The ID of the parent entity.
        """
        parent_field = getattr(self.model, parent_id_field_name)
        statement = select(func.min(self.model.order)).where(parent_field == parent_id)
        result = await db.execute(statement)
        min_order = result.scalar_one_or_none()
        return min_order if min_order is not None else 0

    async def shift_orders_after(
        self,
        db: AsyncSession,
        *,
        parent_id_field_name: str,
        parent_id: uuid.UUID,
        after_order: int,
        shift_value: int,
    ) -> None:
        """
        Shifts the 'order' of items that come after a specific order.
        
        :param parent_id_field_name: The name of the foreign key field on the model.
        :param parent_id: The ID of the parent entity.
        :param after_order: The order value after which to start shifting.
        :param shift_value: The value to add to the order (can be negative).
        """
        parent_field = getattr(self.model, parent_id_field_name)
        statement = (
            update(self.model)
            .where(parent_field == parent_id, self.model.order > after_order)
            .values(order=self.model.order + shift_value)
        )
        await db.execute(statement)
        await db.commit()
