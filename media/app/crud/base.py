
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, get_args
import uuid

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType]):
    def __init__(self, model: Type[ModelType], schema_read: Type[ReadSchemaType]):
        self.model = model
        self.schema_read = schema_read

        generic_args = get_args(self.__class__.__orig_bases__[0])
        if generic_args:
            self.create_schema = generic_args[1]
            self.update_schema = generic_args[2]
        else:
            self.create_schema = CreateSchemaType
            self.update_schema = UpdateSchemaType

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        statement = select(self.model).filter(self.model.id == id)

        result = await db.execute(statement)
        return result.unique().scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).order_by(self.model.id).offset(skip).limit(limit)

        result = await db.execute(statement)
        return result.unique().scalars().all()

    async def get_multi_by_ids(
        self, db: AsyncSession, *, ids: List[Any]
    ) -> List[ModelType]:
        if not ids:
            return []
        
        result = await db.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return result.scalars().all()

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

    async def remove_many(self, db: AsyncSession, *, ids: List[uuid.UUID]) -> int:
        if not ids:
            return 0
        
        stmt = delete(self.model).where(self.model.id.in_(ids))
        
        result = await db.execute(stmt)
        return result.rowcount
