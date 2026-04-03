
'''
This module defines the individual functions (tools) that the LLM Agent 
can decide to use to interact with the application's knowledge base.

These tools are encapsulated within the `EntityAgentTools` class for better
organization and dependency management.
'''

import uuid
from dataclasses import dataclass
from typing import List, Optional

from app.services.graph_manager.entity_graph_manager import EntityGraphManager
from app.crud.crud_entity import crud_entity
from app.crud.crud_entity_fragment import crud_fragment
from app.schemas.entity import EntityCreate
from app.schemas.entity_description_fragment import EntityDescriptionFragmentCreate
from ..vector_store_service.entity_vector_store_service import entity_vector_store_service
from sqlalchemy.ext.asyncio import AsyncSession


# This will be a common data structure returned by search tools
@dataclass
class EntityCandidate:
    """Represents a potential entity match found by a search tool."""
    id: uuid.UUID
    name: str
    type: str
    # A score indicating the confidence of the match (e.g., from vector search)
    score: float

class EntityAgentTools:
    """
    A collection of tools that an LLM agent can use to interact with the
    entity knowledge base of the application.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = entity_vector_store_service
        print("Initializing EntityAgentTools...")

    async def search_for_entity(
        self,
        query: str,
        story_id: uuid.UUID,
        entity_type: Optional[str] = None
    ) -> List[EntityCandidate]:
        """
        Searches for existing entities using a hybrid approach (semantic + direct).
        Returns a ranked list of potential entity matches.
        """
        print(f"AGENT TOOL: Searching for entity matching '{query}' in story {story_id}...")
        # 1. Vector Search (Semantic)
        search_results = self.vector_store.search_entities(
            story_id=story_id,
            query_text=query,
            entity_type=entity_type,
            limit=5
        )
        
        vector_candidates = []
        if search_results:
            for res in search_results:
                vector_candidates.append(EntityCandidate(
                    id=res.id,
                    name=res.metadata['name'],
                    type=res.metadata['type'],
                    score=res.score 
                ))
        print(f"  - Found {len(vector_candidates)} candidates via vector search.")
        # 2. Direct Search (Keyword)
        all_entities_by_type = await EntityGraphManager.get_all_entities_for_story(story_id=story_id)
        direct_candidates = []
        query_lower = query.lower()
        for type_key, entity_list in all_entities_by_type.items():
            if entity_type and type_key.lower() != entity_type.lower():
                continue
            for entity in entity_list:
                if entity['canonical_name'].lower() == query_lower or query_lower in [a.lower() for a in entity['aliases']]:
                    direct_candidates.append(EntityCandidate(
                        id=uuid.UUID(entity['id']),
                        name=entity['canonical_name'],
                        type=type_key,
                        score=1.0  # Perfect score for direct match
                    ))
        print(f"  - Found {len(direct_candidates)} candidates via direct search.")
        # 3. Combine and Rank Results
        combined_candidates = {c.id: c for c in vector_candidates}
        for c in direct_candidates:
            combined_candidates[c.id] = c # Overwrite with direct match if present
        
        final_list = sorted(list(combined_candidates.values()), key=lambda c: c.score, reverse=True)
        print(f"  - Returning {len(final_list)} unique candidates after merging.")
        return final_list

    async def create_new_entity(
        self,
        canonical_name: str,
        entity_type: str,
        story_id: uuid.UUID,
        aliases: Optional[List[str]] = None
    ) -> str:
        """
        Creates a new entity in all required data stores: Postgres, Neo4j, and ChromaDB.
        """
        print(f"AGENT TOOL: Creating new entity '{canonical_name}'...")
        
        entity_in = EntityCreate(
            canonical_name=canonical_name,
            type=entity_type,
            story_id=story_id,
            aliases=aliases or []
        )
        new_entity = await crud_entity.create(self.db, obj_in=entity_in)
        await self.db.commit()

        entity_data_for_graph = {
            "id": str(new_entity.id),
            "story_id": str(story_id),
            "canonical_name": canonical_name,
            "type": entity_type,
            "aliases": aliases or []
        }
        await EntityGraphManager.create_entity_node(entity_data_for_graph)

        collection = self.vector_store.collection
        document = f"Type: {entity_type}. Name: {canonical_name}. Aliases: {', '.join(aliases or [])}."
        
        collection.upsert(
            ids=[str(new_entity.id)],
            documents=[document],
            metadatas=[{"name": canonical_name, "type": entity_type, "story_id": str(story_id)}]
        )

        print(f"  - Successfully created entity with ID {new_entity.id} across all stores.")
        return str(new_entity.id)

    async def add_information_to_entity(
        self,
        entity_id: uuid.UUID,
        fact: str,
        source_node_id: uuid.UUID
    ):
        """
        Adds a new atomic piece of information (a 'fact') to an existing entity.
        This fact is stored in the 'entity_description_fragments' table.
        """
        print(f"AGENT TOOL: Adding fact '{fact}' to entity {entity_id} from source {source_node_id}.")
        
        fragment_in = EntityDescriptionFragmentCreate(
            entity_id=entity_id,
            fragment_text=fact,
            source_node_id=source_node_id
        )
        await crud_fragment.create(self.db, obj_in=fragment_in)
        await self.db.commit()
        
        print(f"  - Successfully added fact to entity {entity_id}.")

    async def link_entity_to_node(
        self,
        entity_id: uuid.UUID,
        node_id: uuid.UUID,
        relationship_type: str = "APPEARS_IN"
    ):
        """
        Creates a relationship in the Neo4j graph between an entity and a narrative node.
        This method wraps the existing functionality in EntityGraphManager.
        """
        print(f"AGENT TOOL: Linking entity {entity_id} to node {node_id} with relationship {relationship_type}.")
        
        await EntityGraphManager.link_entity_to_node(
            entity_id=entity_id,
            target_node_id=node_id
        )
        print("  - Successfully called EntityGraphManager.link_entity_to_node.")
