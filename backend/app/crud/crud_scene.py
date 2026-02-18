from typing import Any, Dict, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .base import CRUDBase
from app.models import Scene
from app.schemas import SceneCreate, SceneUpdate


class CRUDScene(CRUDBase[Scene, SceneCreate, SceneUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Scene | None:
        statement = (
            select(self.model).where(self.model.id == id).options(selectinload(Scene.panels))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Scene]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Scene.panels))
            .order_by(self.model.id)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: SceneCreate) -> Scene:
        db_obj = await super().create(db=db, obj_in=obj_in, commit=False)
        await db.commit()
        full_obj = await self.get(db, id=db_obj.id)
        return full_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Scene, obj_in: Union[SceneUpdate, Dict[str, Any]]
    ) -> Scene:
        updated_db_obj = await super().update(db=db, db_obj=db_obj, obj_in=obj_in, commit=True)
        full_obj = await self.get(db, id=updated_db_obj.id)
        return full_obj


scene = CRUDScene(Scene)
