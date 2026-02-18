from typing import Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .base import CRUDBase
from app.models import Story
from app.schemas import StoryCreate, StoryUpdate


class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Story | None:
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(Story.scenes), selectinload(Story.characters))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Story]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Story.scenes), selectinload(Story.characters))
            .order_by(self.model.id)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: StoryCreate) -> Story:
        db_obj = await super().create(db=db, obj_in=obj_in, commit=False)
        # We commit here to get the ID, then fetch the full object
        await db.commit()
        # The `get` method will load the relationships
        full_obj = await self.get(db, id=db_obj.id)
        return full_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Story,
        obj_in: Union[StoryUpdate, Dict[str, Any]]
    ) -> Story:
        # Perform the update
        updated_db_obj = await super().update(db=db, db_obj=db_obj, obj_in=obj_in, commit=True)
        # The `get` method will load the relationships
        full_obj = await self.get(db, id=updated_db_obj.id)
        return full_obj


story = CRUDStory(Story)
