import os
import json
import uuid
import asyncio
from celery import Celery
from kombu import Queue
from sqlalchemy import select
from sqlalchemy.orm import noload


from app.core.config import settings
from app.database import db_helper
from app.core.llm_provider import get_llm
from app.models import Chapter, Scene
from app.schemas import KnowledgeGraph
from app.services.neo4j_service import neo4j_service
from app.services.prompt_service import construct_knowledge_graph_prompt

# --- Celery Configuration ---
celery_app = Celery(
    "analyzer_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.main"]
)

celery_app.conf.task_queues = (Queue('analyzer-queue', routing_key='analyzer.#'),)
celery_app.conf.task_default_queue = 'analyzer-queue'

# --- Celery Task Definition ---

@celery_app.task(name="app.worker.tasks.trigger_analysis_task")
def analyze_story_task(story_id: str):
    """
    Celery task to analyze a story. It runs the async logic inside a new event loop.
    """
    print(f"Received analysis task for story_id: {story_id}")

    async def _run_analysis():
        story_uuid = uuid.UUID(story_id)
        
        try:
            async with db_helper.session_context() as db:
                stmt = (
                    select(Scene)
                    .join(Chapter, Scene.chapter_id == Chapter.id)
                    .where(Chapter.story_id == story_uuid)
                    .options(noload(Scene.frames))
                    .order_by(Chapter.order, Scene.order) 
                )
                result = await db.execute(stmt)
                scenes = result.scalars().all()

                if not scenes:
                    print(f"No scenes found for story_id: {story_id}")
                    return {"status": "complete", "scenes_found": 0}

                print(f"Found {len(scenes)} scenes for story {story_id}. Starting analysis...")

                # Pass the story_id to each scene analysis task
                await asyncio.gather(*[analyze_scene(scene, story_id) for scene in scenes])
                return {"status": "complete", "scenes_analyzed": len(scenes)}

        except Exception as e:
            print(f"An error occurred during the analysis of story {story_id}: {e}")
            raise

    return asyncio.run(_run_analysis())

async def analyze_scene(scene: Scene, story_id: str):
    """
    Analyzes a single scene to extract a knowledge graph and scopes it to a story_id.
    """
    print(f"Analyzing Scene {scene.id} for Story {story_id}...")

    try:
        prompt_template, parser = construct_knowledge_graph_prompt(KnowledgeGraph)
        
        prompt_variables = {
            "scene_text": scene.description
        }

        llm = get_llm(settings.google_ai_model_version, temperature=0.2)
        chain = prompt_template | llm | parser        
        
        parsed_dict = await chain.ainvoke(prompt_variables)
        graph_data = KnowledgeGraph(**parsed_dict)

        if graph_data.nodes and graph_data.relationships:
            print(f"  - Extracted {len(graph_data.nodes)} nodes and {len(graph_data.relationships)} relationships.")
            # Pass the story_id to the merging service
            await neo4j_service.merge_graph(graph_data, story_id)
            print(f"  - Successfully merged graph for Scene {scene.id} into Neo4j.")
        else:
            print(f"  - No graph data extracted for Scene {scene.id}.")

    except Exception as e:
        print(f"Error analyzing scene {scene.id} for story {story_id}: {e}")


if __name__ == "__main__":
    print("Starting Celery worker for analysis...")
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '-Q', 'analyzer-queue'
    ])
