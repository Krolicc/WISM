
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .base import CRUDBase
from .mixins import OrderableCRUDMixin
from app.models import Chapter, Scene
from app.schemas import ChapterCreate, ChapterUpdate


class CRUDChapter(OrderableCRUDMixin, CRUDBase[Chapter, ChapterCreate, ChapterUpdate]):
    def _get_eager_loading_options(self) -> list:
        return [selectinload(Chapter.scenes).selectinload(Scene.frames)]

    async def get_max_order_for_story(self, db: AsyncSession, story_id: uuid.UUID) -> int:
        return await self.get_max_order(
            db, parent_id_field_name="story_id", parent_id=story_id
        )

    async def get_min_order_for_story(self, db: AsyncSession, story_id: uuid.UUID) -> int:
        return await self.get_min_order(
            db, parent_id_field_name="story_id", parent_id=story_id
        )

    async def shift_orders_after(
        self, db: AsyncSession, *, story_id: uuid.UUID, after_order: int, shift_value: int
    ) -> None:
        return await super().shift_orders_after(
            db,
            parent_id_field_name="story_id",
            parent_id=story_id,
            after_order=after_order,
            shift_value=shift_value,
        )

crud_chapter = CRUDChapter(Chapter)
