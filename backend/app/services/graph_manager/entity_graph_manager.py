
import uuid
from typing import List, Dict, Any

from app.neo4j_service import neo4j_service
from app.schemas.entity import EntityCreate
from app.schemas.graph.base import EntityNode

class EntityGraphManager:
    """
    A stateless service for all Neo4j graph operations related to entities and their relationships.
    """

@staticmethod
async def get_all_entities_for_story(story_id: uuid.UUID) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetches all canonical entities for a given story, grouped by their type.

    Returns a dictionary where keys are entity types (e.g., 'character')
    and values are lists of entities of that type.
    Example:
    {
        "character": [
            {"id": "...", "canonical_name": "Sherlock", ...}
        ],
        "location": [
            {"id": "...", "canonical_name": "221B Baker St", ...}
        ]
    }
    """
    query = ("""
        MATCH (e:Entity {story_id: $story_id})
        RETURN 
            e.id as id, 
            e.canonical_name as canonical_name, 
            e.aliases as aliases,
            [label IN labels(e) WHERE label <> 'Entity'][0] AS type
    """)

    all_entities_flat = await neo4j_service.execute_query(query, params={'story_id': str(story_id)})

    grouped_entities = {member.value: [] for member in EntityType}

    # Group the entities by type
    for entity in all_entities_flat:
        entity_type_str = entity.get('type', '').lower()
        if entity_type_str in grouped_entities:
            entity_data = {
                "id": entity.get("id"),
                "canonical_name": entity.get("canonical_name"),
                "aliases": entity.get("aliases", []),
            }
            grouped_entities[entity_type_str].append(entity_data)

    return grouped_entities


    @staticmethod
    async def link_entity_to_node(
        entity_id: uuid.UUID,
        target_node_id: int
    ):
        """
        Links entities to a target node, ensuring that the most specific appearance is recorded.
        It removes any less specific APPEARS_IN relationships to parent nodes.
        """
        if not entity_ids:
            return

        print(f"GraphManager: Linking {len(entity_ids)} entities to {target_node_id}")

        entity_id_strs = [str(eid) for eid in entity_ids]

        query = ("""
            MATCH (target) WHERE target.id = $target_node_id
            MATCH (entity:Entity) WHERE entity.id = $entity_id
            MERGE (target)-[:APPEARS_IN]->(entity)
        """)

        try:
            await neo4j_service.execute_query(query, params={
                'target_node_id': target_node_id,
                'entity_ids': entity_id_strs
            })
            print(f"  - Successfully executed linking query.")
        except Exception as e:
            print(f"  - Error during entity linking: {e}")

