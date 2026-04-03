
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.core.graph_crud_service import graph_crud_service

from .collect_parent_context import collect_parent_context
from .collect_sibling_context import collect_sibling_context
from .collect_vector_context import collect_vector_context

async def assemble_full_narrative_context(
    self, 
    db: AsyncSession, 
    *, 
    parent_id: uuid.UUID,
    crud_manager: CRUDBase,
    is_self_context: bool = True,
    item_id: Optional[uuid.UUID] = None,
    user_prompt: str = ""
) -> str:
    """
        Assembles a rich, narrative-aware context prompt for the LLM.
        This is the new "brain" of the generation process.
    """

    parent_context = await collect_parent_context(db, parent_id=parent_id)
    
    current_item_parts = []
    story_id = await graph_crud_service.get_story_id(parent_id)
    vector_query = user_prompt + "\n" + parent_context
    vector_context = await collect_vector_context(story_id=story_id, query_text=vector_query, exclude_id=item_id)
    sibling_context = "Нет повествовательного контекста."

    if not (item_id):
        narrative_anchor_id = await graph_crud_service.find_narrative_anchor_id(parent_id)
        sibling_context = await collect_sibling_context(db, item_id=narrative_anchor_id)
    else:
        sibling_context = await collect_sibling_context(db, item_id=item_id)
        
        if is_self_context:
            db_item = await crud_manager.get(db, id=item_id)
            item_title = getattr(db_item, 'title', None)
            item_content = getattr(db_item, 'description', getattr(db_item, 'overview', None))

            if item_title:
                current_item_parts.append(f"The title of the item we are working on is: '{item_title}'.")
            if item_content:
                current_item_parts.append(f"Its current content/summary is: \"{item_content}\"")
    
    if current_item_parts:
        current_item_context = "\n".join(current_item_parts)
    else:
        current_item_context = "We are creating a brand new item, so there is no existing content for it. Your task is to create it from scratch based on the user's instruction."

    # Combine all contexts into a final, structured prompt.
    final_prompt = f"""**Current Item Context (What we are working on):**
        {current_item_context}
    
        **Parent Context (The story so far):**
        {parent_context}
        
        **Sibling Context (What happens immediately before and after):**
        {sibling_context}

        **Семантически похожие элементы истории:**
        {vector_context}

        **User's Task:**
        {user_prompt}
    """
    return final_prompt