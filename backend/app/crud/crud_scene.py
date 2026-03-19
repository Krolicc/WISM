
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .base import CRUDBase
from .mixins import OrderableCRUDMixin
from app.models import Chapter, Scene
from app.schemas import SceneCreate, SceneUpdate


class CRUDScene(OrderableCRUDMixin, CRUDBase[Scene, SceneCreate, SceneUpdate]):
    def _get_eager_loading_options(self) -> list:
        return [selectinload(Scene.frames)]

    async def get_max_order_for_chapter(self, db: AsyncSession, chapter_id: uuid.UUID) -> int:
        return await self.get_max_order(
            db, parent_id_field_name="chapter_id", parent_id=chapter_id
        )

    async def get_min_order_for_chapter(self, db: AsyncSession, chapter_id: uuid.UUID) -> int:
        return await self.get_min_order(
            db, parent_id_field_name="chapter_id", parent_id=chapter_id
        )

    async def shift_orders_after(
        self, db: AsyncSession, *, chapter_id: uuid.UUID, after_order: int, shift_value: int
    ) -> None:
        return await super().shift_orders_after(
            db,
            parent_id_field_name="chapter_id",
            parent_id=chapter_id,
            after_order=after_order,
            shift_value=shift_value,
        )

    async def delete_by_chapter_id(
        self, db: AsyncSession, *, parent_id: uuid.UUID
    ) -> None:
        statement = delete(self.model).where(self.model.chapter_id == parent_id)
        await db.execute(statement)
        await db.commit()

    async def get_multi_by_story(
        self, db: AsyncSession, *, story_id: int
    ) -> list[Scene]:
        """
        Retrieve all scenes for a specific story by joining through chapters.
        The scenes are ordered by their ID to ensure chronological sequence.
        """
        statement = (
            select(self.model)
            .join(Chapter, self.model.chapter_id == Chapter.id)
            .where(Chapter.story_id == story_id)
            .order_by(self.model.id)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_scene_context(self, db: AsyncSession, scene_id: uuid.UUID) -> dict:
        statement = (
            select(Scene)
            .where(Scene.id == scene_id)
            .options(
                selectinload(Scene.chapter).selectinload(
                    Chapter.story
                )
            )
        )
        result = await db.execute(statement)
        scene = result.unique().scalar_one_or_none()

        if not scene:
            return None

        return {"story": scene.chapter.story, "chapter": scene.chapter, "scene": scene}


crud_scene = CRUDScene(Scene)
