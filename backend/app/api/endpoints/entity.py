
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_helper
from app.services.entity.entity_extractor import EntityExtractor
from app.services.graph_manager import GraphManager # Assuming GraphManager can fetch node text

router = APIRouter()

# --- Request Models ---

class NodeAnalysisRequest(BaseModel):
    story_id: uuid.UUID
    source_node_id: int

# --- API Endpoints ---

@router.post("/analyze-node", status_code=status.HTTP_202_ACCEPTED)
async def analyze_node_for_entities(
    *, 
    request: NodeAnalysisRequest,
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """
    Analyzes the text content of a specific graph node (e.g., a Scene)
    to extract, match, and save entity information.
    """
    # 1. Get the text content from the source node in Neo4j
    try:
        node_text = await GraphManager.get_node_text(request.source_node_id)
        if not node_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content for node {request.source_node_id} not found or is empty."
            )
    except Exception as e:
        # This could be a connection error or if the node doesn't exist
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve node text from graph database: {e}"
        )

    # 2. Trigger the main entity processing workflow
    # This process is now self-contained and doesn't need a background task for this endpoint
    try:
        await EntityExtractor.process_text_and_link_entities(
            db=db,
            text=node_text,
            story_id=request.story_id,
            source_node_id=request.source_node_id
        )
    except Exception as e:
        # Catch potential errors during the extraction/saving process
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during entity processing: {e}"
        )

    return {"message": f"Entity analysis for node {request.source_node_id} has been successfully completed."}


@router.post("/{entity_id}/regenerate-description", status_code=status.HTTP_200_OK)
async def regenerate_entity_description(
    *, 
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(db_helper.session_getter)
):
    """
    Manually triggers the regeneration and caching of an entity's description
    from its collected fragments.
    """
    try:
        new_description = await EntityExtractor.generate_and_cache_description(db=db, entity_id=entity_id)
        
        if new_description is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with id {entity_id} not found."
            )
            
        return {
            "message": "Description regenerated successfully.",
            "entity_id": entity_id,
            "new_description": new_description
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during description regeneration: {e}"
        )
