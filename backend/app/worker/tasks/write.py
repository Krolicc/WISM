
import uuid
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.database import db_helper
from app.schemas import orchestration as schemas
from app.worker.tasks.base import NotificationTask
from app.worker.tasks.helpers import run_content_rewriting_task
from app.services import (
    arc_service,
    chapter_service,
    scene_service,
    frame_service,
)

@celery_app.task(
    name=schemas.OrchestrationTask.REWRITE_ARC_CONTENT.value,
    base=NotificationTask,
    bind=True,
    service=arc_service)
def rewrite_arc_content(self, payload: Dict[str, Any]):
    return self.run_async(run_content_rewriting_task(
        payload,
        params_class=schemas.RewriteArcContentParams,
        service=self.service,
        item_ids_field="arc_ids",
        prompt_field="writing_prompt"
    ))


@celery_app.task(name=schemas.OrchestrationTask.REWRITE_CHAPTER_CONTENT.value, base=NotificationTask, bind=True, service=chapter_service)
def rewrite_chapter_content(self, payload: Dict[str, Any]):
    return self.run_async(run_content_rewriting_task(
        payload,
        params_class=schemas.RewriteChapterContentParams,
        service=self.service,
        item_ids_field="chapter_ids",
        prompt_field="writing_prompt"
    ))


@celery_app.task(name=schemas.OrchestrationTask.REWRITE_SCENE_CONTENT.value, base=NotificationTask, bind=True, service=scene_service)
def rewrite_scene_content(self, payload: Dict[str, Any]):
    return self.run_async(run_content_rewriting_task(
        payload,
        params_class=schemas.RewriteSceneContentParams,
        service=self.service,
        item_ids_field="scene_ids",
        prompt_field="writing_prompt"
    ))


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_FRAMES_CONTENT.value, base=NotificationTask, bind=True, service=frame_service)
def write_frame_content(self, payload: Dict[str, Any]):
    return self.run_async(run_content_writing_task(
        payload,
        params_class=schemas.GenerateFramesContentParams,
        service=self.service,
        item_ids_field="frame_ids",
        prompt_field="writing_prompt"
    ))


@celery_app.task(name=schemas.OrchestrationTask.GENERATE_FRAME_IMAGE.value, base=NotificationTask, bind=True, service=frame_service)
def generate_frame_image(self, payload: Dict[str, Any]):
    """Special-case task to generate an image for a single Frame."""
    async def _run():
        params = schemas.GenerateFrameImageParams(**payload['params'])
        frame_id = uuid.UUID(params.frame_id)
        
        async with db_helper.session_context() as db:
            result = await self.service.generate_image(
                db=db, 
                frame_id=frame_id, 
                prompt=params.style_prompt
            )
        return {"status": "success", "frame_id": str(frame_id), "image_url": result.image_url}
    return self.run_async(_run())
