
import uuid
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.database import db_helper
from app.schemas import orchestration as schemas
from app.worker.tasks.base import NotificationTask
from app.worker.tasks.helpers import run_skeleton_generation_task
from app.services import (
    story_service,
    arc_service,
    chapter_service,
    scene_service,
    frame_service,
)

# Note: The 'service' kwarg in the task decorator is a custom addition to provide the
# service object to the task body, which is then passed to the helper.

@celery_app.task(name=schemas.OrchestrationTask.DECOMPOSE_TEXT_TO_SKELETON.value, base=NotificationTask, bind=True, service=story_service)
def decompose_text_to_skeleton(self, payload: Dict[str, Any]):
    """
    This task is slightly different and doesn't fit the standard generation helper.
    It's a one-off task for a single story.
    """
    async def _run():
        params = schemas.DecomposeTextToSkeletonParams(**payload['params'])
        story_id = uuid.UUID(payload['story_id'])
        
        # This task is unique and requires direct implementation.
        async with db_helper.session_context() as db:
            await self.service.decompose_text_to_skeleton(
                db=db,
                story_id=story_id,
                full_text=params.full_text
            )
        return {"status": "success", "details": "Story decomposition initiated."}
    return self.run_async(_run())


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_ARCS_SKELETON.value, base=NotificationTask, bind=True, service=arc_service)
def generate_arcs_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_generation_task(
        payload,
        params_class=schemas.GenerateArcsSkeletonParams,
        service=self.service,
        parent_ids_field="story_ids",
        prompt_field="user_prompt",
        count_field="num_arcs"
    ))


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_CHAPTERS_SKELETON.value, base=NotificationTask, bind=True, service=chapter_service)
def generate_chapters_skeleton(self, payload: Dict[str, Any]):
    print("Start 'generate_chapters_skeleton'")
    return self.run_async(run_skeleton_generation_task(
        payload,
        params_class=schemas.GenerateChaptersSkeletonParams,
        service=self.service,
        parent_ids_field="arc_ids",
        prompt_field="prompt",
        count_field="num_chapters"
    ))


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_SCENES_SKELETON.value, base=NotificationTask, bind=True, service=scene_service)
def generate_scenes_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_generation_task(
        payload,
        params_class=schemas.GenerateScenesSkeletonParams,
        service=self.service,
        parent_ids_field="chapter_ids",
        prompt_field="prompt",
        count_field="num_scenes"
    ))


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_FRAMES_SKELETON.value, base=NotificationTask, bind=True, service=frame_service)
def generate_frames_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_generation_task(
        payload,
        params_class=schemas.GenerateFramesSkeletonParams,
        service=self.service,
        parent_ids_field="scene_ids",
        prompt_field="prompt",
        count_field="num_frames"
    ))
