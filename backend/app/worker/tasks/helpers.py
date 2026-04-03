
import asyncio
import uuid
from typing import Dict, Any, List

from app.database import db_helper

# ===================================================================
# 1. HELPER FOR SKELETON GENERATION TASKS
# ===================================================================

async def run_skeleton_generation_task(
    payload: Dict[str, Any],
    params_class: Any,
    service: Any,
    parent_ids_field: str,
    prompt_field: str,
    count_field: str
):
    """
    Generic helper for tasks that generate child items for a list of parents.
    (e.g., generate chapters for arcs).
    """
    params = params_class(**payload['params'])
    parent_ids = getattr(params, parent_ids_field)
    prompt = getattr(params, prompt_field, '')
    count = getattr(params, count_field)
    
    # Dynamically get the correct generation method from the service
    # (e.g., generate_arcs_from_prompt, generate_chapters_from_prompt)
    service_method = getattr(service, f"generate_{service.model_name}s_from_prompt")
    
    parent_kwarg_name = parent_ids_field.replace("_ids", "_id")
    
    results = []
    for p_id in parent_ids:
        async with db_helper.session_context() as db:
            result = await service_method(
                db=db,
                prompt=prompt,
                **{count_field: count},
                **{parent_kwarg_name: p_id}
            )
            results.append(result)


    flat_results = [item for sublist in results for item in sublist]
    return {"status": "success", "items_created": len(flat_results)}

# ===================================================================
# 2. HELPER FOR CONTENT WRITING TASKS
# ===================================================================

async def run_content_rewriting_task(
    payload: Dict[str, Any],
    params_class: Any,
    service: Any,
    item_ids_field: str,
    prompt_field: str
):
    """
    Generic helper for tasks that write content for a list of existing items.
    (e.g., write content for chapters).
    """
    params = params_class(**payload['params'])
    item_ids = getattr(params, item_ids_field)
    prompt = getattr(params, prompt_field, '')
    
    service_method = getattr(service, f"rewrite_{service.model_name}_content")

    item_kwarg_name = item_ids_field.replace("_ids", "_id")
    
    results = []
    for item_id_str in item_ids:
        async with db_helper.session_context() as db:
            result = await service_method(
                db=db,
                prompt=prompt,
                **{item_kwarg_name: item_id_str}
            )
            results.append(result)

    return {"status": "success", "items_updated": len(results)}


# ===================================================================
# 3. HELPER FOR NEW ITEM INSERT AND SKELETON GENERATE TASKS
# ===================================================================

async def run_new_item_insert_and_skeleton_generate_task(
    payload: Dict[str, Any],
    params_class: Any,
    service: Any,
    parent_id_field: str,
    insert_after_ids_field: str,
    prompt_field: str,
    count_field: str
):
    """
    Generic helper for tasks that generate child items for a list of parents.
    (e.g., generate chapters for arcs).
    """
    params = params_class(**payload['params'])
    parent_id = getattr(params, parent_id_field)
    insert_after_ids = getattr(params, insert_after_ids_field)
    prompt = getattr(params, prompt_field, '')
    count = getattr(params, count_field)
    
    # Dynamically get the correct generation method from the service
    # (e.g., generate_arcs_from_prompt, generate_chapters_from_prompt)
    service_method = getattr(service, f"insert_{service.model_name}s_and_generate_skeleton_from_prompt")
    
    results = []
    for insert_after_id in insert_after_ids:
        async with db_helper.session_context() as db:
            result = await service_method(
                db=db,
                prompt=prompt,
                count=count,
                parent_id=parent_id,
                insert_after_id=insert_after_id
            )
            results.append(result)


    flat_results = [item for sublist in results for item in sublist]
    return {"status": "success", "items_inserted": len(flat_results)}

# ===================================================================
# 4. HELPER FOR SKELETON REGENERATE TASKS
# ===================================================================

async def run_skeleton_regenerate_task(
    payload: Dict[str, Any],
    params_class: Any,
    service: Any,
    item_ids_field: str,
    prompt_field: str,
):
    params = params_class(**payload['params'])
    item_ids = getattr(params, item_ids_field)
    prompt = getattr(params, prompt_field, '')
    
    # Dynamically get the correct generation method from the service
    # (e.g., generate_arcs_from_prompt, generate_chapters_from_prompt)
    service_method = getattr(service, f"regenerate_{service.model_name}_skeleton_from_prompt")
    
    item_kwarg_name = item_ids_field.replace("_ids", "_id")
    
    results = []
    for item_id_str in item_ids:
        async with db_helper.session_context() as db:
            result = await service_method(
                db=db,
                prompt=prompt,
                **{item_kwarg_name: item_id_str}
            )
            results.append(result)


    flat_results = [item for sublist in results for item in sublist]
    return {"status": "success", "items_regenerated": len(flat_results)}