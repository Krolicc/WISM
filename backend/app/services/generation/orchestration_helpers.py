
import uuid
from typing import Any, Dict, Optional, Type, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..providers.vector_store_service import VectorStoreService, SearchResult
from app.crud import crud_chapter, crud_scene
from app.crud.base import CRUDBase


async def get_hierarchical_metadata(
    db: AsyncSession, db_obj: Any, model_name: str
) -> Dict[str, int]:
    """
    Traverses up the hierarchy from a given object to collect the 'order' values
    of its parents, creating a chronological signature.
    """

    try:
        if model_name == "frame":
            scene = await crud_scene.get(db, id=db_obj.scene_id)
            chapter = await crud_chapter.get(db, id=scene.chapter_id)
            return {
                "chapter_order": chapter.order,
                "scene_order": scene.order,
                "frame_order": db_obj.order,
            }
        elif model_name == "scene":
            chapter = await crud_chapter.get(db, id=db_obj.chapter_id)
            return {
                "chapter_order": chapter.order, 
                "scene_order": db_obj.order
            }
        elif model_name == "chapter":
            return {
                "chapter_order": db_obj.order
            }
    
    except AttributeError:
        return {}
    
    return {}

async def get_hierarchical_orders_for_new_item(
    db: AsyncSession, model_name: str, parent_id: uuid.UUID, order: int
) -> Dict[str, int]:
    """ 
    Computes the hierarchical order for a *new* item that hasn't been created yet.
    This is used to filter the context for generation to only include past events.
    """
    try:
        if model_name == "frame":
            scene = await crud_scene.get(db, id=parent_id) # parent_id is scene_id
            chapter = await crud_chapter.get(db, id=scene.chapter_id)
            return {
                "chapter_order": chapter.order,
                "scene_order": scene.order,
                "frame_order": order,
            }
        elif model_name == "scene":
            chapter = await crud_chapter.get(db, id=parent_id) # parent_id is chapter_id
            return {
                "chapter_order": chapter.order, 
                "scene_order": order
            }
        elif model_name == "chapter":
            return {
                "chapter_order": order
            }
    except (AttributeError, KeyError):
        return {}

    return {}


async def upsert_document_in_vector_store(
    db: AsyncSession,
    vector_store_service: VectorStoreService,
    *,
    db_obj: Any,
    model_name: str,
    parent_id_field_name: str,
    parent_id: uuid.UUID,
    get_story_id: callable,
):
    """
    Adds or updates a document in the vector store with hierarchical order metadata,
    skipping for 'frame' models.
    """
    if model_name == "frame":
        print(f"  - Upsert frame (skipping indexing).")
        return

    print(f"  - Upsert {model_name}: '{db_obj.title}'.")
    try:
        hierarchical_orders = await get_hierarchical_metadata(db, db_obj, model_name)
        story_id = await get_story_id(db, parent_id)

        metadata = {
            "story_id": str(story_id),
            "model_name": model_name,
            "title": db_obj.title,
            f"{parent_id_field_name}": str(getattr(db_obj, parent_id_field_name)),
            **hierarchical_orders,
        }

        vector_store_service.upsert_document(
            doc_id=str(db_obj.id), text=db_obj.description, metadata=metadata
        )
        print(f"  - Indexed {model_name} '{db_obj.title}' in vector store.")
    except Exception as e:
        print(f"  - Failed to index {model_name} '{db_obj.title}': {e}")


def construct_prompt_template(
    model_name: str, pydantic_schema: Type[BaseModel], list_name: Optional[str] = None
) -> tuple[ChatPromptTemplate, JsonOutputParser]:
    """Constructs the chat prompt template with dynamic system instructions."""
    parser = JsonOutputParser(pydantic_object=pydantic_schema)

    # System prompt templates remain the same
    if list_name:
        system_template = (
            f"You are a world-renowned author and creative genius, specializing in crafting compelling narratives. "
            f"Your task is to expand upon a given idea, generating a series of {model_name}s that bring the story to life.\n\n"
            f"**Contextual Information:**\n{{context}}\n\n"
            f"**Instructions:**\n"
            f"1. Carefully analyze the user's prompt which contains the core idea or context.\n"
            f"2. Generate exactly {{count}} distinct {model_name}(s).\n"
            f"3. For each {model_name}, provide all the required fields as specified in the JSON schema.\n"
            f"4. Ensure the generated content is creative, coherent, and logically flows from the provided context.\n"
            f"5. Your entire output must be a single, valid JSON object. The main key of this object should be '{list_name}', "
            f"and its value should be an array of the {model_name} objects.\n\n"
            f"**JSON Schema:**\n{{format_instructions}}\n\n"
            f"Begin generation now."
        )
    else:
        system_template = (
            f"You are a world-renowned author and creative genius, specializing in crafting compelling narratives. "
            f"Your task is to flesh out a given idea into a single, well-defined {model_name}.\n\n"
            f"**Contextual Information:**\n{{context}}\n\n"
            f"**Instructions:**\n"
            f"1. Carefully analyze the user's prompt which contains the core idea or context.\n"
            f"2. Generate one single {model_name}.\n"
            f"3. Provide all the required fields as specified in the JSON schema.\n"
            f"4. Ensure the generated content is creative, detailed, and directly addresses the user's prompt.\n"
            f"5. Your entire output must be a single, valid JSON object that adheres to the provided schema.\n\n"
            f"**JSON Schema:**\n{{format_instructions}}\n\n"
            f"Begin generation now."
        )

    user_template = "{prompt}"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", user_template)]
    )
    return prompt_template, parser


def format_context_from_docs(docs: List[SearchResult]) -> str:
    """Formats a list of search results into a readable, chronological context string."""
    if not docs:
        return "No additional context was provided."

    # Sort documents based on their hierarchical order
    def get_sort_key(doc: SearchResult):
        metadata = doc.metadata
        return (
            metadata.get("chapter_order", 0),
            metadata.get("scene_order", 0),
            metadata.get("frame_order", 0),
        )

    sorted_docs = sorted(docs, key=get_sort_key)

    context_items = []
    current_chapter = None
    current_scene = None

    for doc in sorted_docs:
        meta = doc.metadata
        title = meta.get('title', 'Untitled')
        model_name = meta.get('model_name', 'item')

        # Announce chapter change
        if model_name == 'chapter' and meta.get("chapter_order") != current_chapter:
            current_chapter = meta.get("chapter_order")
            context_items.append(f"In Chapter {current_chapter} titled '{title}':")
            current_scene = None # Reset scene when chapter changes

        # Announce scene change
        elif model_name == 'scene' and meta.get("scene_order") != current_scene:
            if meta.get("chapter_order") != current_chapter:
                current_chapter = meta.get("у")
                # We need a chapter title here, but it might not be in the doc.
                # This is a limitation if we only get scenes in the search results.
                context_items.append(f"In a later chapter (order {current_chapter}):")

            current_scene = meta.get("scene_order")
            context_items.append(f"  During the scene '{title}':")

        # Add the actual content
        indent = "    " if current_scene is not None else "  "
        context_items.append(f"{indent}- Summary: {doc.page_content}")

    if not context_items:
        return "No structured context could be built from the search results."

    return "Here is some relevant context from the story, in chronological order:\n" + "\n".join(context_items)

async def calculate_order(
    db: AsyncSession,
    crud_manager: CRUDBase,
    parent_id_field_name: str,
    parent_id: uuid.UUID,
    count: int,
    before_id: Optional[uuid.UUID],
    after_id: Optional[uuid.UUID],
) -> tuple[int, int]:
    """Calculates the starting order and step for new items, handling collisions."""
    MAX_RETRIES = 5

    get_max_order_fn = getattr(
        crud_manager, f"get_max_order_for_{parent_id_field_name.replace('_id','')}"
    )
    get_min_order_fn = getattr(
        crud_manager, f"get_min_order_for_{parent_id_field_name.replace('_id','')}"
    )
    shift_orders_fn = getattr(crud_manager, "shift_orders_after")

    for _ in range(MAX_RETRIES):
        max_order = (
            await get_max_order_fn(db, **{parent_id_field_name: parent_id})
        ) or 0
        min_order = (
            await get_min_order_fn(db, **{parent_id_field_name: parent_id})
        ) or 0

        if before_id and after_id:
            before_obj = await crud_manager.get(db, id=before_id)
            after_obj = await crud_manager.get(db, id=after_id)
            if not before_obj or not after_obj:
                raise ValueError("Adjacent item(s) not found.")

            start_order = before_obj.order
            calculated_step = (after_obj.order - start_order) // (count + 1)

            if calculated_step < 10:
                shift_amount = (count + 1) * 100
                await shift_orders_fn(
                    db,
                    parent_id=parent_id,
                    after_order=start_order,
                    shift_value=shift_amount,
                )
                continue  # Retry with the new ordering
            return start_order, calculated_step

        elif before_id:  # Inserting at the end
            before_obj = await crud_manager.get(db, id=before_id)
            if not before_obj or before_obj.order != max_order:
                raise ValueError(f"'{before_id}' is not the last item.")
            return before_obj.order, 100

        elif after_id:  # Inserting at the beginning
            after_obj = await crud_manager.get(db, id=after_id)
            if not after_obj or after_obj.order != min_order:
                raise ValueError(f"'{after_id}' is not the first item.")

            start_order = 0
            calculated_step = after_obj.order // (count + 1)
            if calculated_step < 10:
                shift_amount = (count + 1) * 100
                await shift_orders_fn(
                    db, parent_id=parent_id, after_order=0, shift_value=shift_amount
                )
                continue  # Retry with the new ordering
            return start_order, calculated_step
        else:  # Inserting in an empty list
            return max_order, 100

    raise RuntimeError(f"Failed to find a suitable order after {MAX_RETRIES} attempts.")
