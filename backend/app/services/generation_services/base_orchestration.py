
import abc
import uuid
from typing import Any, Dict, List, Optional, Type
from types import SimpleNamespace

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, crud
from app.crud.base import CRUDBase
from .tools.llm.run_llm_generation import run_llm_generation

from app.services.vector_store_service.comic_vector_store_service import comic_vector_store_service
from app.core.graph_crud_service import graph_crud_service
from app.core.neo4j_service import neo4j_service
from app.schemas.graph import base as graph_schemas

GRAPH_NODE_SCHEMA_REGISTRY = {
    "story": graph_schemas.StoryNode,
    "arc": graph_schemas.ArcNode,
    "chapter": graph_schemas.ChapterNode,
    "scene": graph_schemas.SceneNode,
    "frame": graph_schemas.FrameNode,
    "entity": graph_schemas.EntityNode,
}

class BaseOrchestrationService(abc.ABC):
    """
    An abstract base class for services that generate hierarchical story content.

    It provides a set of common, non-recursive methods to be used by Celery tasks:
    - `generate_skeleton_from_prompt`: Creates new items based on a prompt.
    - `write_full_content`: Fills in the main content of an existing item.
    - `refine_existing_items`: Rewrites existing items based on a refinement prompt.

    Each service (e.g., ArcService, ChapterService) must implement the abstract
    properties to define its specific model, CRUD manager, and schemas.
    """

    # --- Abstract Properties (Unchanged, this structure is good) ---
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
        """A dictionary containing Pydantic schemas for LLM parsing."""
        ...

    @property
    @abc.abstractmethod
    def parent_service(self) -> Optional["BaseOrchestrationService"]:
        """The orchestration service for the parent entity, if any."""
        ...

    @property
    @abc.abstractmethod
    def child_service(self) -> Optional["BaseOrchestrationService"]:
        """The orchestration service for the child entity, if any."""

    # --- Helper Methods (Kept for reusability) ---

    async def _create_and_save_object(
        self,
        db: AsyncSession,
        *,
        item_data: Dict[str, Any],
        parent_id: uuid.UUID,
        previous_sibling_id: Optional[uuid.UUID] = None,
        next_sibling_id: Optional[uuid.UUID] = None
    ) -> Any:
        """
        Создает объект в PG, узел и связи в Neo4j, и индексирует его.
        """
        print(f"\n--- DB SAVE DEBUG for {self.model_name} ---")
        print(f"[Input Data]: {item_data}")
        print(f"Parent id: {parent_id}")

        try:
            validated_create_data = self.crud_manager.create_schema(**item_data)
            new_item = await self.crud_manager.create(db, obj_in=validated_create_data)

            print(f"[PostgreSQL]: Successfully created {self.model_name} with ID: {new_item.id}")

            # 2. Создаем узел в Neo4j
            story_id = await graph_crud_service.get_story_id(parent_id)
            GraphNodeSchema = GRAPH_NODE_SCHEMA_REGISTRY[self.model_name]
            
            node_data = GraphNodeSchema(
                id=new_item.id,
                story_id=story_id,
                title=new_item.title,
            )
            
            await graph_crud_service.create_node(
                node_label=self.model_name,
                node_data=node_data
            )

            print(f"[Neo4j]: Successfully created {self.model_name} node.")

            # 3. Создаем связи в Neo4j
            await graph_crud_service.create_relationship(
                start_node_id=parent_id,
                end_node_id=new_item.id,
                relationship_type="CONTAINS"
            )

            print(f"[Neo4j]: Successfully created :CONTAINS relationship from parent {parent_id}.")


            if previous_sibling_id:
                await graph_crud_service.create_relationship(
                    start_node_id=previous_sibling_id,
                    end_node_id=new_item.id,
                    relationship_type="NEXT"
                )

            if next_sibling_id:
                await graph_crud_service.create_relationship(
                    start_node_id=new_item.id,
                    end_node_id=next_sibling_id,
                    relationship_type="NEXT"
                )

            # 4. Индексируем в векторном хранилище (без изменений)
            await comic_vector_store_service.upsert_document_in_vector_store(
                db_obj=new_item,
                model_name=self.model_name,
                story_id=story_id
            )

            print(f"[VectorDB]: Successfully upserted document for {new_item.id}.")
            print("--- DB SAVE SUCCESS ---\n")
            
            return new_item
        except Exception as e:
            print(f"---!!!! DB SAVE FAILED !!!! ---")
            print(f"An error occurred during the save process for {self.model_name}: {e}")
            print(f"--------------------------\n")
            # Depending on the desired transactional behavior, you might want to
            # roll back the PG creation here, but for now, we just log the failure.
            return None

    async def _recursive_pg_delete(self, db: AsyncSession, *, ids_to_delete: Set[uuid.UUID]):
        """
        Рекурсивно вызывает дочерние сервисы для удаления записей из PostgreSQL,
        обеспечивая удаление "снизу-вверх" для соблюдения foreign key constraints.
        """
        if self.child_service:
            await self.child_service._recursive_pg_delete(db, ids_to_delete=ids_to_delete)
        
        if ids_to_delete:
            await self.crud_manager.remove_many(db, ids=list(ids_to_delete))

    async def _cascade_delete_children(self, db: AsyncSession, *, parent_id: uuid.UUID):
        """
        Находит ВСЕХ потомков для parent_id и каскадно удаляет их из всех 
        трех баз данных, используя рекурсивный подход для PostgreSQL.
        """
        query_find_ids = """
        MATCH (parent {id: $parent_id})-[:CONTAINS*1..]->(descendant)
        RETURN collect(descendant.id) as ids
        """
        result = await neo4j_service.execute_query(query_find_ids, {'parent_id': str(parent_id)})
        descendant_ids_str = result[0]['ids'] if result and result[0]['ids'] else []

        if not descendant_ids_str:
            return


        query_delete_graph = "MATCH (n) WHERE n.id IN $ids DETACH DELETE n"
        await neo4j_service.execute_query(query_delete_graph, {'ids': descendant_ids_str})

        await comic_vector_store_service.delete(ids=descendant_ids_str)
        
        descendant_ids_uuid = {uuid.UUID(id_str) for id_str in descendant_ids_str}
        await self._recursive_pg_delete(db, ids_to_delete=descendant_ids_uuid)
        
        await db.flush()

    # --- NEW Public Orchestration Methods (Replaces old generate/regenerate) ---

    async def generate_skeleton_from_prompt(
        self, db: AsyncSession, *, parent_id: uuid.UUID, prompt: Optional[str] = '', count: int
    ) -> List[Any]:
        """
        Генерирует и вставляет несколько элементов, создавая связи в графе.
        """
        # 1. Находим точку вставки: последнего существующего "брата"
        last_child_of_prev_sibling_id = await graph_crud_service.find_last_child_of_prev_sibling(parent_id)
        first_child_of_next_sibling_id = await graph_crud_service.find_first_child_of_next_sibling(parent_id)

        generation_prompt = prompt
        if not generation_prompt:
            generation_prompt = f"Based on the parent content, generate {count} creative and relevant {self.model_name}s that would logically follow."

        llm_response = await run_llm_generation(
            db=db,
            prompt=generation_prompt,
            task="generate",
            llm_schema=self.llm_schemas["list"],
            crud_manager=self.crud_manager,
            model_name=self.model_name,
            count=count,
            parent_id=parent_id
        )

        if not llm_response:
            return []

        # 4. Создаем объекты в цикле, выстраивая их в цепочку :NEXT
        list_name = self.llm_schemas["list"]["name"]
        response_items = llm_response.get(list_name, [])
        
        # --- DEBUG LOGGING --- #
        print("\n--- LLM Generation DEBUG ---")
        print(f"Items: {response_items}")
        # --- END DEBUG LOGGING --- #

        created_items = []
        previous_item_id = last_child_of_prev_sibling_id

        num_items = len(response_items)

        for i, item_data in enumerate(response_items):
            is_last_item = (i == num_items - 1)
            next_sibling_id = first_child_of_next_sibling_id if is_last_item else None

            new_item = await self._create_and_save_object(
                db,
                item_data=item_data,
                parent_id=parent_id,
                previous_sibling_id=previous_item_id,
                next_sibling_id=next_sibling_id
            )
            created_items.append(new_item)
            previous_item_id = new_item.id
        
        return created_items

    async def rewrite_content(
    self, db: AsyncSession, *, item_id: uuid.UUID, prompt: Optional[str] = ''
    ) -> Any:
        """
        Генерирует полное 'description' для существующего элемента.
        """
        db_item = await self.crud_manager.get(db, id=item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail=f"{self.model_name} not found")

        parent_id = await graph_crud_service.get_parent_id(item_id)
        if not parent_id:
            parent_id = item_id 

        generation_prompt = prompt
        if not generation_prompt:
            generation_prompt = f"Based on the title and overview of this {self.model_name}, write its full content in a compelling and engaging literary style."


        llm_response = await run_llm_generation(
            db=db,
            prompt=writing_prompt,
            task="rewrite",
            llm_schema=self.llm_schemas["content"],
            crud_manager=self.crud_manager,
            model_name=self.model_name,
            item_id=item_id
        )
        
        if llm_response is None:
            print(f"LLM service returned None for {self.model_name} {item_id}. Aborting refinement.")
            return db_item

        new_description = llm_response.get('description', None)
        if not new_description:
            return db_item

        updated_item = await self.crud_manager.update(db, id=item_id, obj_in={"description": new_description})
        
        story_id = await graph_crud_service.get_story_id(item_id)
        if story_id:
            await comic_vector_store_service.upsert_document_in_vector_store(
                model_name=self.model_name,
                db_obj=updated_item,
                story_id=story_id
            )
        
        return updated_item

    async def regenerate_skeleton_from_prompt(
        self, db: AsyncSession, *,
        item_id: uuid.UUID, prompt: str
    ) -> List[Any]:

        await self._cascade_delete_children(db, parent_id=item_id)

        await self.rewrite_content(
            db,
            item_ids=[item_id],
            writing_prompt=prompt
        )

        newly_created_children = await self.generate_skeleton_from_prompt(
            db,
            parent_id=item_id,
            prompt=f"Создай {5} {self.child_model_name}, основываясь на обновленном содержании родителя.",
            count=5
        )

        return newly_created_children

    async def insert_item_and_generate_skeleton_from_prompt(
        self, db: AsyncSession, *,
        parent_id: uuid.UUID, prompt: str, count: int,
        previous_sibling_id: Optional[uuid.UUID] = None
    ) -> Any:
        # --- Шаг 1: РЕКУРСИВНЫЙ РАЗРЫВ СВЯЗЕЙ ---

        # 1a. Находим соседей.
        left_sibling_id = previous_sibling_id
        right_sibling_id = None
        if left_sibling_id:
            query_find_right = "MATCH (left {id: $left_id})-[:NEXT]->(right) RETURN right.id as right_id"
            result = await self.graph_db.execute_query(query_find_right, {'left_id': str(left_sibling_id)})
            if result and result[0].get('right_id'):
                right_sibling_id = uuid.UUID(result[0]['right_id'])

        # 1b. Если есть оба соседа, запускаем рекурсивный разрыв.
        if left_sibling_id and right_sibling_id:
            await graph_crud_service.recursive_break_next_links(left_sibling_id, right_sibling_id)

        # --- Шаг 2: ГЕНЕРАЦИЯ И ВСТАВКА ТЕКУЩЕГО ЭЛЕМЕНТА ---

        # 2a. Генерируем контент для нового элемента (как в rewrite_content)
        new_item_data = await run_llm_generation(
            db=db,
            prompt=prompt,
            task="create",
            llm_schema=self.llm_schemas["item"],
            crud_manager=self.crud_manager,
            model_name=self.model_name,
            parent_id=parent_id
        )

        if not new_item_data:
            raise ValueError("LLM failed to generate data for the new item.")

        # 2b. Вставляем новый элемент МЕЖДУ соседями
        new_item = await self._create_and_save_object(
            db,
            model_data=new_item_data,
            parent_id=parent_id,
            previous_sibling_id=left_sibling_id,
            next_sibling_id=right_sibling_id
        )

        # --- Шаг 3: ГЕНЕРАЦИЯ ДОЧЕРНЕГО СКЕЛЕТА ---
        if num_children > 0:
            await self.generate_skeleton_from_prompt(
                db,
                parent_id=new_item["desciption"],
                prompt=prompt,
                count=count
            )

        return new_item

    async def execute_action_chain(
        self, db: AsyncSession, *, actions: List[Dict[str, Any]], previous_step_output: Any = None
    ) -> Dict[str, Any]:
        """
        Recursively executes a chain of actions, delegating to child services as needed.
        This implements the "relay race" pattern.
        """
        if not actions:
            return {"status": "completed"}
        current_action = actions[0]
        remaining_actions = actions[1:]
        target_model = current_action.get("target_model")
        if not target_model:
            raise ValueError(f"Action {current_action.get('action')} is missing required 'target_model' field.")

        if target_model == self.model_name:
            action_name = current_action.get("action")
            action_method = getattr(self, action_name, None)
            if not callable(action_method):
                raise ValueError(f"Unknown action '{action_name}' on service for '{self.model_name}'.")
            action_args = {k: v for k, v in current_action.items() if k not in ["action", "target_model"]}
            action_args['db'] = db
            # Chain input from previous step if specified
            prompt_from_key = action_args.pop("prompt_from_output", None)
            if prompt_from_key and previous_step_output:
                action_args["prompt"] = getattr(previous_step_output, prompt_from_key)
            print(f"[Chain] Executing '{action_name}' on '{self.model_name}'...")
            try:
                result = await action_method(**action_args)

                return await self.execute_action_chain(
                    db, actions=remaining_actions, previous_step_output=result
                )
            except Exception as e:
                raise RuntimeError(f"Execution failed at step '{action_name}' on '{self.model_name}': {e}")
        # 2. If the action is for a child, delegate the whole chain.
        elif self.child_service:
            print(f"[Chain] Delegating to child service '{self.child_service.model_name}'...")
            return await self.child_service.execute_action_chain(
                db, actions=actions, previous_step_output=previous_step_output
            )
        else:
            raise ValueError(
                f"Action for '{target_model}' cannot be handled by '{self.model_name}' service, and no child service is available."
            )