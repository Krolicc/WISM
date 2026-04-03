
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from chromadb.api.client import Client
from chromadb.api.models.Collection import Collection

from app.core.vector_store_provider import get_vector_store_client


@dataclass
class SearchResult:
    """A more generic search result data structure."""
    id: uuid.UUID
    document: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    score: Optional[float] = None


class BaseVectorStore:
    """
    A base class for interacting with a specific ChromaDB collection.
    It encapsulates the generic logic for upserting, searching, and deleting vectors.
    """

    def __init__(self, collection_name: str, client: Client = get_vector_store_client()):
        if not collection_name:
            raise ValueError("A collection_name must be provided.")
        self.client = client
        self.collection = self._get_or_create_collection(collection_name)
        print(f"Initialized BaseVectorStore for collection: '{collection_name}'")

    def _get_or_create_collection(self, name: str) -> Collection:
        """Gets or creates a collection in ChromaDB."""
        return self.client.get_or_create_collection(name=name)

    def upsert(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def search(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where_clause: Optional[Dict[str, Any]] = None,
    ) -> List[List[SearchResult]]:
        """
        Performs a generic similarity search with an optional metadata filter.
        Returns a list of lists, where each inner list corresponds to a query text.
        """
        if not where_clause:
            where_clause = {}
            
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where_clause,
            include=["metadatas", "documents", "distances"]
        )

        # Unpack results into a structured format
        all_search_results = []
        for i in range(len(results["ids"])):
            query_results = []
            if results["ids"][i]:
                for j in range(len(results["ids"][i])):
                    distance = results["distances"][i][j]
                    score = 1 / (1 + distance)
                    query_results.append(SearchResult(
                        id=uuid.UUID(results["ids"][i][j]),
                        document=results["documents"][i][j],
                        metadata=results["metadatas"][i][j],
                        distance=distance,
                        score=score
                    ))
            all_search_results.append(query_results)
        
        return all_search_results

    def delete(self, ids: List[str]) -> None:
        """Deletes documents from the collection by their IDs."""
        if not ids:
            return
        self.collection.delete(ids=ids)
