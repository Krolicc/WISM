
import uuid
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.schemas import orchestration as schemas
from app.worker.tasks.helpers import run_new_item_insert_and_skeleton_generate_task
from app.services import (
    arc_service, 
    chapter_service, 
    scene_service
)

@celery_app.task(
    name=schemas.OrchestrationTask.INSERT_NEW_ARC_AND_GENERATE_SKELETON.value,
    base=schemas.NotificationTask,
    bind=True,
    service=arc_service
)
def insert_new_arc_and_generate_skeleton(self, payload: Dict[str, Any]):
    """
    Celery task to insert a new Arc between existing ones and generate its skeleton.
    """
    return self.run_async(run_new_item_insert_and_skeleton_generate_task(
        payload,
        params_class=schemas.InsertNewArcAndGenerateSkeletonParams,
        service=self.service,
        parent_id_field="parent_id",
        insert_after_ids_field="insert_after_ids",
        prompt_field="prompt",
        count_field="count"
    ))

@celery_app.task(
    name=schemas.OrchestrationTask.INSERT_NEW_CHAPTER_AND_GENERATE_SKELETON.value,
    base=schemas.NotificationTask,
    bind=True,
    service=chapter_service
)
def insert_new_chapter_and_generate_skeleton(self, payload: Dict[str, Any]):
    """
    Celery task to insert a new Chapter between existing ones and generate its skeleton.
    """
    return self.run_async(run_new_item_insert_and_skeleton_generate_task(
        payload,
        params_class=schemas.InsertNewChapterAndGenerateSkeletonParams,
        service=self.service,
        parent_id_field="parent_id",
        insert_after_id_field="insert_after_id",
        prompt_field="prompt",
        count_field="count"
    ))

@celery_app.task(
    name=schemas.OrchestrationTask.INSERT_NEW_SCENE_AND_GENERATE_SKELETON.value,
    base=schemas.NotificationTask,
    bind=True,
    service=scene_service
)
def insert_new_scene_and_generate_skeleton(self, payload: Dict[str, Any]):
    """
    Celery task to insert a new Scene between existing ones and generate its skeleton.
    """
    return self.run_async(run_new_item_insert_and_skeleton_generate_task(
        payload,
        params_class=schemas.InsertNewSceneAndGenerateSkeletonParams,
        service=self.service,
        parent_id_field="parent_id",
        insert_after_id_field="insert_after_id",
        prompt_field="prompt",
        count_field="count"
    ))
