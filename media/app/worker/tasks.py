
import asyncio
from app.core.celery_app import celery_app
from app.core.database import db_helper
from app.crud import crud_entity, crud_frame, crud_generation
from app.schemas.generation import GenerationCreate
from app.services.prompt_parser import prompt_parser_service
from app.services.comfyui_service import comfyui_service
from app.models.enums import GenerationStatus


async def _process_item(item_id, crud_item, generation_type):
    """Helper function to process a single item (entity or frame)."""
    async with db_helper.session_context() as session:
        # 1. Create a generation record with PENDING status
        generation_create = GenerationCreate(
            related_id=item_id, 
            type=generation_type, 
            status=GenerationStatus.PENDING
        )
        generation_record = await crud_generation.create(db=session, obj_in=generation_create)

        try:
            # 2. Get the item (entity/frame) from the database
            item = await crud_item.get(db=session, id=item_id)
            if not item:
                raise ValueError(f"{generation_type.capitalize()} with id {item_id} not found.")

            # 3. Parse the detailed_prompt
            prompt_str = prompt_parser_service.parse(item.detailed_prompt)
            if not prompt_str:
                raise ValueError("Parsed prompt string is empty.")

            # 4. Generate the image
            # Assuming a default or pre-configured seed for now
            image_bytes = await comfyui_service.generate_image(prompt=prompt_str, seed=123)

            # 5. TODO: Save the image_bytes to a file and get the path
            image_path = f"path/to/generated/{generation_type}_{item_id}.png"

            # 6. Update the generation record to COMPLETED
            await crud_generation.update(
                db=session, 
                db_obj=generation_record, 
                obj_in={"status": GenerationStatus.COMPLETED, "image_path": image_path}
            )

        except Exception as e:
            print(f"Error processing {generation_type} {item_id}: {e}")
            # 7. Update the generation record to FAILED
            if generation_record:
                await crud_generation.update(
                    db=session, 
                    db_obj=generation_record, 
                    obj_in={"status": GenerationStatus.FAILED, "error_message": str(e)}
                )

@celery_app.task(name="app.worker.tasks.generate_entity_images", bind=True)
def generate_entity_images_task(self, payload: dict):
    """Celery task to generate images for a list of entities."""
    ids = payload.get("ids", [])
    if not ids:
        return {"status": "skipped", "reason": "No IDs provided"}

    loop = asyncio.get_event_loop()
    for entity_id in ids:
        loop.run_until_complete(_process_item(entity_id, crud_entity, "entity"))

    return {"status": "completed", "processed_ids": ids}


@celery_app.task(name="app.worker.tasks.generate_frame_images", bind=True)
def generate_frame_images_task(self, payload: dict):
    """Celery task to generate images for a list of frames."""
    ids = payload.get("ids", [])
    if not ids:
        return {"status": "skipped", "reason": "No IDs provided"}

    loop = asyncio.get_event_loop()
    for frame_id in ids:
        loop.run_until_complete(_process_item(frame_id, crud_frame, "frame"))
        
    return {"status": "completed", "processed_ids": ids}

