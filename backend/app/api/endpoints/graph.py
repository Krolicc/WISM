
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.neo4j_service import neo4j_service

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

# @router.get(
#     "/full",
#     response_model=FullGraphResponse,
#     summary="Fetch the entire knowledge graph",
#     description="Retrieves all nodes and relationships from the Neo4j database, formatted for frontend visualization."
# )
# async def get_full_graph():
#     """
#     Endpoint to fetch the complete knowledge graph from Neo4j.
#     It retrieves raw graph data from the service layer and then transforms it
#     into the required API response format. This ensures a clean separation
#     of concerns and a consistent data structure for the client.
#     """
#     raw_graph_data = await neo4j_service.get_full_graph()

#     formatted_nodes = [
#         GraphNode(**node_data) for node_data in raw_graph_data.get("nodes", [])
#     ]
#     formatted_relationships = [
#         GraphRelationship(**rel_data) for rel_data in raw_graph_data.get("relationships", [])
#     ]
#     return FullGraphResponse(nodes=formatted_nodes, relationships=formatted_relationships)

@router.get(
    "/{story_id}/hierarchy",
    response_model=Dict[str, Any],
    summary="Получить иерархию одной истории",
    description="Возвращает полную структуру одной истории в виде вложенного JSON-объекта, идеально подходящего для отображения в виде дерева."
)
async def get_story_hierarchy(
    story_id: uuid.UUID,
):
    """
    Этот эндпоинт получает полную иерархию для одной указанной истории.
    Он использует метод `export_story_as_dict` из сервиса Neo4j,
    который эффективно собирает всю структуру данных за один запрос.
    """
    # 1. Вызываем нужный метод сервиса, передавая ему story_id
    story_data = await neo4j_service.export_story_as_dict(story_id=story_id)

    # 2. Проверяем, был ли найден результат. Если нет - возвращаем ошибку 404.
    if not story_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"История с ID: {story_id} не найдена."
        )

    # 3. Если все в порядке, возвращаем полученный словарь
    return story_data
# @router.delete(
#     "/{story_id}",
#     status_code=status.HTTP_200_OK,
#     summary="Delete Graph Data for a Specific Story"
# )
# async def delete_story_graph(
#     story_id: uuid.UUID,
#     neo4j_service: Neo4jService = Depends(get_neo4j_service)
# ):
#     await neo4j_service.delete_data_by_story_id(str(story_id))
#     return {"message": f"Graph data for story {story_id} has been deleted."}

# @router.delete(
#     "/",
#     status_code=status.HTTP_200_OK,
#     summary="Delete All Graph Data (Use with Caution)"
# )
# async def delete_all_graphs(
#     neo4j_service: Neo4jService = Depends(get_neo4j_service)
# ):
#     await neo4j_service.delete_all_data()
#     return {"message": "All graph data has been successfully deleted."}
