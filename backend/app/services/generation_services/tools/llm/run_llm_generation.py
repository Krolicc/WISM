import uuid
from typing import Dict, Any, Optional, Union, List

from sqlalchemy.ext.asyncio import AsyncSession

from .content_generator import generate_content_from_prompt
from ..collect_context import assemble_full_narrative_context


async def run_llm_generation(
    self,
    db: AsyncSession,
    prompt: str,
    task: str,
    llm_schema: Dict[str, Any],
    crud_manager: CRUDBase,
    model_name: str,
    count: Optional[int] = None,
    parent_id: Optional[uuid.UUID] = None,
    item_id: Optional[uuid.UUID] = None
) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
    """
    Унифицированная функция для вызова LLM.
    Собирает контекст и вызывает generate_content_from_prompt.
    """
    is_self_context = item_id is not None
    
    full_context = await assemble_full_narrative_context(
        db=db,
        parent_id=parent_id,
        is_self_context=is_self_context,
        crud_manager=crud_manager,
        item_id=item_id,
        user_prompt=prompt
    )

    # 2. Вызываем LLM для генерации.
    llm_response = await generate_content_from_prompt(
        task=task,
        prompt=prompt,
        context=full_context,
        count=count,
        llm_schema=llm_schema,
        model_name=model_name,
    )

    return llm_response