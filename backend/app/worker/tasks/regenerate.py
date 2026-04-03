
import uuid
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.schemas import orchestration as schemas
from app.database import db_helper
from .base import NotificationTask
from app.worker.tasks.helpers import run_skeleton_regenerate_task
from app.services import (
    arc_service, 
    chapter_service, 
    scene_service
)

@celery_app.task(
    name=schemas.OrchestrationTask.REGENERATE_ARC_SKELETON.value,
    base=NotificationTask,
    bind=True,
    service=arc_service
)
def regenerate_arc_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_regenerate_task(
        payload,
        params_class=schemas.RegenerateArcSkeletonParams,
        service=self.service,
        item_ids_field="arc_ids",
        prompt_field="prompt"
    ))

@celery_app.task(
    name=schemas.OrchestrationTask.REGENERATE_CHAPTER_SKELETON.value,
    base=NotificationTask,
    bind=True,
    service=chapter_service
)
def regenerate_chapter_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_regenerate_task(
        payload,
        params_class=schemas.RegenerateChapterSkeletonParams,
        service=self.service,
        item_ids_field="chapter_ids",
        prompt_field="prompt"
    ))

@celery_app.task(
    name=schemas.OrchestrationTask.REGENERATE_SCENE_SKELETON.value,
    base=NotificationTask,
    bind=True,
    service=scene_service
)
def regenerate_scene_skeleton(self, payload: Dict[str, Any]):
    return self.run_async(run_skeleton_regenerate_task(
        payload,
        params_class=schemas.RegenerateSceneSkeletonParams,
        service=self.service,
        item_ids_field="scene_ids",
        prompt_field="prompt"
    ))
