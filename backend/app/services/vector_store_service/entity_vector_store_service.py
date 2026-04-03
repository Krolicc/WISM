
import uuid
from typing import List, Optional, Dict, Any

from app.services.providers.base_vector_store import BaseVectorStore, SearchResult


class EntityVectorStoreService(BaseVectorStore):
    """
    A specialized vector store service for searching within story entities.
    It inherits from BaseVectorStore and provides a search method
    tailored for finding entities within a specific story, optionally filtered by type.
    """

    def __init__(self):
        # Initialize with the specific collection name for entities.
        super().__init__(collection_name="entities")

    def search_entities(
        self,
        *,
        story_id: uuid.UUID,
        query_text: str,
        entity_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[SearchResult]:
        """
        Searches for similar entities within a given story.

        This method builds a 'where' clause to scope the search to the story
        and optionally to a specific entity type, then calls the generic search.
        """
        # 1. Start building the filter clause with the mandatory story_id
        where_clause: Dict[str, Any] = {"story_id": {"$eq": str(story_id)}}

        # 2. If an entity_type is provided, add it to the filter
        if entity_type:
            # We create a compound filter using $and
            where_clause = {
                "$and": [
                    where_clause,
                    {"type": {"$eq": entity_type}}
                ]
            }

        # 3. Call the generic search method from the base class
        search_results = super().search(
            query_texts=[query_text], n_results=limit, where_clause=where_clause
        )

        # 4. Return the first (and only) list of results, as we only pass one query.
        return search_results[0] if search_results else []


# Create a singleton-like instance for easy access.
entity_vector_store_service = EntityVectorStoreService()
