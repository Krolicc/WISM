
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app import models, crud
from app.core.graph_crud_service import graph_crud_service

async def _run_entity_analysis_agent(db: AsyncSession, item: Any):
    """
    Attempts to run the entity analysis agent on the content of a given item.
    Only runs for specific model types (e.g., 'frame').
    Failures are caught and logged without crashing the main process.
    """
    # Мы хотим запускать дорогой анализ только для самого детального контента.
    # В нашей иерархии это 'frame'.
    if not hasattr(item, 'description') or not item.description:
        return

    print(f"\\n--- AGENT TRIGGER: Detected content update for {item.id}. ---")
    try:
        from app.services.agent_service.executor import AgentExecutor

        if not hasattr(item, 'story_id') or not item.story_id:
             # Если story_id не был подгружен вместе с item, получим его.
             story_id = await graph_crud_service.get_story_id(item.id)
             if not story_id:
                 print(f"AGENT SKIPPED: Could not determine story_id for item {item.id}.")
                 return
        else:
            story_id = item.story_id

        agent_executor = AgentExecutor(
            db=db,
            story_id=story_id,
            source_node_id=item.id
        )
        await agent_executor.run(text_to_analyze=item.description)
        print(f"--- AGENT FINISHED: Analysis complete for {item.id}. ---")

    except Exception as e:
        # Ловим все ошибки, чтобы падение агента не сломало основной процесс.
        print(f"---!!!! AGENT ERROR !!!! ---")
        print(f"Agent execution failed for item {item.id}: {e}")
        print(f"--------------------------\\n")