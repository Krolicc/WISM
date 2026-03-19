from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from chromadb.api.client import Client
from chromadb.api.models.Collection import Collection

from app.core.vector_store_provider import get_vector_store_client


@dataclass
class SearchResult:
    page_content: str
    metadata: Dict[str, Any]


class VectorStoreService:
    """Service for interacting with the vector store (ChromaDB)."""

    def __init__(self, client: Client = get_vector_store_client()):
        self.client = client
        self.collection = self._get_or_create_collection("comic_content")
        self.order_keys = ["chapter_order", "scene_order", "frame_order"]

    def _get_or_create_collection(self, name: str) -> Collection:
        """Gets or creates a collection in ChromaDB."""
        return self.client.get_or_create_collection(name=name)

    def upsert_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """Adds or updates a document in the collection."""
        self.collection.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def _build_hierarchical_filter(
        self, order_filter: Dict[str, int]
    ) -> Dict[str, Any]:
        """Constructs a ChromaDB $or filter to find documents that appeared before a given hierarchical order."""
        relevant_orders = {
            key: order_filter[key] for key in self.order_keys if key in order_filter
        }

        or_conditions = []
        # Create a chain of conditions for each level of the hierarchy (chapter, scene, etc.)
        for i, key in enumerate(relevant_orders):
            current_level_conditions = []
            # Add equality constraints for all parent levels
            for j in range(i):
                parent_key = self.order_keys[j]
                current_level_conditions.append(
                    {parent_key: {"$eq": relevant_orders[parent_key]}}
                )

            # Add the less-than constraint for the current level
            current_level_conditions.append({key: {"$lt": relevant_orders[key]}})

            if len(current_level_conditions) > 1:
                or_conditions.append({"$and": current_level_conditions})
            else:
                or_conditions.append(current_level_conditions[0])

        if len(or_conditions) > 1:
            return {"$or": or_conditions}
        elif or_conditions:
            return or_conditions[0]
        else:
            return {}

    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        order_filter: Optional[Dict[str, int]] = None,
    ) -> List[SearchResult]:
        """
        Searches for similar documents, with optional filtering by metadata and a
        hierarchical order to exclude future documents.
        """
        where_clause = filter.copy() if filter else {}

        if order_filter:
            hierarchical_filter = self._build_hierarchical_filter(order_filter)
            if hierarchical_filter:
                if where_clause:
                    print(f"{where_clause} -- {hierarchical_filter}")
                    # Combine existing filters (e.g., story_id) with the order filter
                    where_clause = {"$and": [where_clause, hierarchical_filter]}
                else:
                    where_clause = hierarchical_filter

        final_filter = where_clause if where_clause else None

        results = self.collection.query(
            query_texts=[query], n_results=k, where=final_filter
        )

        # Unpack the results from ChromaDB's format into a list of SearchResult objects
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        search_results = [
            SearchResult(page_content=documents[i], metadata=metadatas[i])
            for i in range(len(ids))
        ]

        return search_results
    
    def get_all_vectors(self) -> Dict[str, Any]:
        """Retrieves all vectors from the collection."""
        results = self.collection.get()
        return results