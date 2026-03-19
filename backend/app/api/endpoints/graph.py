
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.services.neo4j_service import Neo4jService, get_neo4j_service

router = APIRouter()

# --- Pydantic Schemas for API Response ---
# These models define the structure of the JSON that will be sent to the frontend.

class GraphNode(BaseModel):
    # This is the internal element ID from Neo4j, used by visualization libraries
    # to uniquely identify a node and draw relationships.
    element_id: str
    labels: List[str]
    properties: Dict[str, Any]

class GraphRelationship(BaseModel):
    # These fields must contain the element_id of the source and target nodes.
    source: str
    target: str
    type: str
    properties: Dict[str, Any]

class FullGraphResponse(BaseModel):
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]

# --- API Endpoint ---

@router.get(
    "/full",
    response_model=FullGraphResponse,
    summary="Fetch the entire knowledge graph",
    description="Retrieves all nodes and relationships from the Neo4j database, formatted for frontend visualization."
)
async def get_full_graph(
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
):
    """
    Endpoint to fetch the complete knowledge graph from Neo4j.
    It retrieves raw graph data from the service layer and then transforms it
    into the required API response format. This ensures a clean separation
    of concerns and a consistent data structure for the client.
    """
    raw_graph_data = await neo4j_service.get_full_graph()

    formatted_nodes = [
        GraphNode(**node_data) for node_data in raw_graph_data.get("nodes", [])
    ]
    formatted_relationships = [
        GraphRelationship(**rel_data) for rel_data in raw_graph_data.get("relationships", [])
    ]
    return FullGraphResponse(nodes=formatted_nodes, relationships=formatted_relationships)

@router.get(
    "/{story_id}",
    response_model=FullGraphResponse,
    summary="Fetch the entire knowledge graph",
    description="Retrieves all nodes and relationships from the Neo4j database, formatted for frontend visualization."
)
async def get_story_specific_graph(
    story_id: uuid.UUID,
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
):
    """
    Endpoint to fetch a knowledge graph filtered by story_id.
    """
    raw_graph_data = await neo4j_service.get_graph_by_story_id(str(story_id))
   
    if not raw_graph_data.get("nodes"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No graph data found for story_id: {story_id}")
   
    formatted_nodes = [
        GraphNode(**node_data) for node_data in raw_graph_data.get("nodes", [])
    ]
   
    formatted_relationships = [
        GraphRelationship(**rel_data) for rel_data in raw_graph_data.get("relationships", [])
    ]


    return FullGraphResponse(nodes=formatted_nodes, relationships=formatted_relationships)

@router.delete(
    "/{story_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Graph Data for a Specific Story"
)
async def delete_story_graph(
    story_id: uuid.UUID,
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
):
    await neo4j_service.delete_data_by_story_id(str(story_id))
    return {"message": f"Graph data for story {story_id} has been deleted."}
@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Delete All Graph Data (Use with Caution)"
)
async def delete_all_graphs(
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
):
    await neo4j_service.delete_all_data()
    return {"message": "All graph data has been successfully deleted."}
