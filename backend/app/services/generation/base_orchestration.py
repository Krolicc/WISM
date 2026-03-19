
import abc
import uuid
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.config import settings
from app.crud.base import CRUDBase
from ..providers.llm_provider import get_llm
from ..providers.vector_store_service import VectorStoreService
from .orchestration_helpers import (
    upsert_document_in_vector_store,
    calculate_order,
    construct_prompt_template,
    get_hierarchical_orders_for_new_item,
    format_context_from_docs,
)

class BaseOrchestrationService(abc.ABC):
    """
    An abstract base class for orchestration services that handles the generic logic
    for content generation, regeneration, and insertion with ordering.
    """
    def __init__(self):
        self.vector_store_service = VectorStoreService()

    # --- Abstract Properties to be Implemented by Subclasses ---

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """The user-friendly name of the model (e.g., 'chapter', 'scene')."""
        ...

    @property
    @abc.abstractmethod
    def crud_manager(self) -> CRUDBase:
        """The CRUD manager for the associated model."""
        ...

    @property
    @abc.abstractmethod
    def llm_schemas(self) -> Dict[str, Any]:
        """
        A dictionary containing Pydantic schemas for LLM parsing.
        Expected format:
        {
            "single": Type[BaseModel],
            "list": {"schema": Type[BaseModel], "name": str}
        }
        """
        ...

    @property
    @abc.abstractmethod
    def create_schema(self) -> Type[BaseModel]:
        """The Pydantic schema for creating a new database object."""
        ...
    
    @property
    @abc.abstractmethod
    def update_schema(self) -> Type[BaseModel]:
        """The Pydantic schema for updating an existing database object."""
        ...

    @property
    @abc.abstractmethod
    def parent_id_field_name(self) -> str:
        """The name of the foreign key field linking to the parent object."""
        ...

    @property
    @abc.abstractmethod
    def child_service(self) -> Optional["BaseOrchestrationService"]:
        """The orchestration service for the child entity, if any."""
        ...
    
    async def _get_story_id(self, db: AsyncSession, parent_id: uuid.UUID) -> uuid.UUID:
        """
        Retrieves the story ID from the parent object.
        This base implementation raises an error. It must be overridden by any
        service that is a child of another service (e.g., Chapter, Scene).
        """
        raise NotImplementedError(
            f"The service for '{self.model_name}' must implement the "
            f"'_get_story_id' method to trace back to the story."
        )
        
    # --- Private Helper Methods ---
    async def _get_context_for_prompt(
        self, 
        db: AsyncSession, 
        *, 
        prompt: str, 
        parent_id: uuid.UUID,
        order_details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Retrieves relevant, chronologically-aware context from the vector store.
        """

        order_filter = None
        if order_details and order_details.get("parent_id") and order_details.get("order") is not None:
            order_filter = await get_hierarchical_orders_for_new_item(
                db, self.model_name, order_details["parent_id"], order_details["order"]
            )

        try:
            story_id = await self._get_story_id(db, parent_id)
            similar_docs = self.vector_store_service.search(
                query=prompt,
                k=5,
                filter={"story_id": str(story_id)},
                order_filter=order_filter
            )

            return format_context_from_docs(similar_docs)
        except Exception as e:
            print(f"  - Could not perform vector search for context: {e}")
            return "An error occurred while fetching context."

    async def _create_and_save_object(
        self, db: AsyncSession, *, item_data: BaseModel, parent_id: uuid.UUID, order: int, child_count: int = 3
    ) -> Any:
        """Creates an object, saves it, generates children, and indexes it."""
        create_data = {**item_data.dict(), self.parent_id_field_name: parent_id, "order": order}
        new_item = await self.crud_manager.create(db, obj_in=self.create_schema(**create_data))
        
        await upsert_document_in_vector_store(
            db,
            self.vector_store_service,
            db_obj=new_item,
            model_name=self.model_name,
            parent_id_field_name=self.parent_id_field_name,
            parent_id=parent_id,
            get_story_id=self._get_story_id
        )

        if self.child_service:
            await self.child_service.generate(
                db, parent_id=new_item.id, idea=item_data.description, count=child_count
            )
        
        refreshed_item = await self.crud_manager.get(db, id=new_item.id)
        return refreshed_item

    # --- Core LLM Interaction Logic ---

    async def _generate_content_from_prompt(
        self, db: AsyncSession, *, prompt: str, count: int, generation_mode: str, 
        temperature: float = 0.7, 
        parent_id: Optional[uuid.UUID] = None,
        order_details: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseModel]:
        """
        Generates content from an LLM based on the specified mode ('single' or 'list').
        """
        if generation_mode == "list":
            schema_info = self.llm_schemas["list"]
            pydantic_schema = schema_info["schema"]
            list_name = schema_info["name"]
        else:
            pydantic_schema = self.llm_schemas["single"]
            list_name = None

        context_str = "No additional context was provided."
        if parent_id:
            context_str = await self._get_context_for_prompt(
                db, prompt=prompt, parent_id=parent_id, order_details=order_details
            )

        prompt_template, parser = construct_prompt_template(self.model_name, pydantic_schema, list_name)
        
        prompt_variables = {
            "count": count, 
            "prompt": prompt,
            "context": context_str,
            "format_instructions": parser.get_format_instructions()
        }

        try:
            llm = get_llm(settings.google_ai_model_version, temperature=temperature)
            chain = prompt_template | llm | parser
            response_data = await chain.ainvoke(prompt_variables)
            return pydantic_schema(**response_data)
        except Exception as e:
            print(f"An error occurred in LLM generation for {self.model_name}: {e}")
            return None

    # --- Public Orchestration Methods ---

    async def regenerate(
        self, db: AsyncSession, *, id: uuid.UUID, idea: str, child_count: int = 3
    ) -> Optional[Any]:
        """Deletes old child content and generates new content for an object."""
        db_obj = await self.crud_manager.get(db=db, id=id)
        if not db_obj:
            raise OrchestrationError(f"Object with id {id} not found for level {level}.")

        print(f"Regenerating content for {self.model_name} '{getattr(db_obj, 'title', id)}'...")

        if self.child_service:
            delete_children_method = getattr(self.child_service.crud_manager, f"delete_by_{self.child_service.parent_id_field_name}")
            deleted_count = await delete_children_method(db, parent_id=db_obj.id)
            print(f"  - Deleted {deleted_count} old child {self.child_service.model_name}(s).")

        parent_id = getattr(db_obj, self.parent_id_field_name, None)
        
        order_details = {"parent_id": parent_id, "order": db_obj.order}

        llm_response = await self._generate_content_from_prompt(
            db, prompt=idea, count=1, generation_mode="single", parent_id=parent_id, order_details=order_details
        )
        if not llm_response:
            print(f"Failed to generate new content for {self.model_name}. Aborting regeneration.")
            return None

        db.expire(db_obj)

        update_data = self.update_schema(**llm_response.dict())
        updated_obj = await self.crud_manager.update(db, id=id, obj_in=update_data)
        
        await upsert_document_in_vector_store(
            db,
            self.vector_store_service,
            db_obj=updated_obj,
            model_name=self.model_name,
            parent_id_field_name=self.parent_id_field_name,
            parent_id=parent_id,
            get_story_id=self._get_story_id
        )

        if self.child_service:
            print(f"  - Generating {child_count} new child {self.child_service.model_name}(s)...")
            await self.child_service.generate(
                db,
                parent_id=updated_obj.id,
                idea=update_data.description,
                count=child_count,
            )

        refreshed_obj = await self.crud_manager.get(db, id=updated_obj.id)
        print(f"Content regeneration for {self.model_name} '{getattr(refreshed_obj, 'title', refreshed_obj.id)}' complete.")
        return refreshed_obj

    async def generate(
        self, db: AsyncSession, *, parent_id: uuid.UUID, idea: str, count: int,
        before_id: Optional[uuid.UUID] = None, after_id: Optional[uuid.UUID] = None,
        temperature: float = 0.7, child_count: int = 3
    ) -> List[Any]:
        """Generates and inserts one or more items with correct ordering and recursively generates children."""
        start_order, step = await calculate_order(
            db, self.crud_manager, self.parent_id_field_name, parent_id, count, before_id, after_id
        )

        # For now, we will use the order of the first new item for context generation.
        # A more advanced implementation could run generation for each item sequentially.
        first_item_order = start_order + step
        order_details = {"parent_id": parent_id, "order": first_item_order}

        llm_response = await self._generate_content_from_prompt(
            db, prompt=idea, count=count, temperature=temperature, 
            generation_mode="list", parent_id=parent_id, order_details=order_details
        )
        if not llm_response:
            return []

        list_name = self.llm_schemas["list"]["name"]
        response_items = getattr(llm_response, list_name, [])
        if not response_items or len(response_items) != count:
            print(f"LLM returned {len(response_items)} items, but expected {count}. Aborting.")
            return []

        created_items = []
        for i, item_data in enumerate(response_items):
            new_order = start_order + (i + 1) * step
            new_item = await self._create_and_save_object(
                db, item_data=item_data, parent_id=parent_id, order=new_order, child_count=child_count
            )
            created_items.append(new_item)
        
        return created_items
