
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import uuid

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _get_eager_loading_options(self) -> list:
        """
        Returns a list of SQLAlchemy loader options for eager loading.
        This method is intended to be overridden by subclasses.
        """
        return []

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        statement = select(self.model).filter(self.model.id == id)
        options = self._get_eager_loading_options()
        if options:
            statement = statement.options(*options)

        result = await db.execute(statement)
        return result.unique().scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        options = self._get_eager_loading_options()
        if options:
            statement = statement.options(*options)

        result = await db.execute(statement)
        return result.unique().scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType, commit: bool = True
    ) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        if not commit:
            return db_obj
        
        await db.commit()
        full_obj = await self.get(db, id=db_obj.id)
        return full_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> ModelType:
        db_obj = await self.get(db, id=id)
        if not db_obj:
            return None

        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        if not commit:
            return db_obj

        await db.commit()
        updated_obj = await self.get(db, id=db_obj.id)
        return updated_obj

    async def delete(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
