import uuid

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from chromadb.api.client import Client
from chromadb.api.models.Collection import Collection

from app.core.vector_store_provider import get_vector_store_client
from app.services.providers.base_vector_store import BaseVectorStore, SearchResult

class ComicVectorStoreService(BaseVectorStore):
    def __init__(self):
        super().__init__(collection_name="comic_content")

    def search_by_story(
        self,
        *,
        story_id: uuid.UUID,
        query_text: str,
        limit: int = 5,
        exclude_id: Optional[uuid.UUID] = None,
    ) -> List[SearchResult]:
        """
        Searches for similar documents within a given story, with an option to exclude one ID.

        This method builds the specific 'where' clause for this collection and then
        calls the generic search method from the base class.
        """
        # 1. Build the filter clause for ChromaDB, specific to this collection's data structure
        where_clause = {"story_id": {"$eq": str(story_id)}}

        if exclude_id:
            # This assumes that the document's own 'id' is stored in its metadata.
            where_clause = {
                "$and": [
                    where_clause,
                    {"metadata.id": {"$ne": str(exclude_id)}}  # Note: query metadata
                ]
            }

        # 2. Call the generic search method from the base class
        # We are only passing one query_text, so we expect one list of results back.
        search_results = super().search(
            query_texts=[query_text], n_results=limit, where_clause=where_clause
        )

        # 3. Return the first (and only) list of results.
        return search_results[0] if search_results else []

    async def upsert_document_in_vector_store(
        db_obj: Any,
        model_name: str,
        story_id: uuid.UUID,
    ):
        if model_name == "frame":
            print(f"  - Upsert frame (skipping indexing).")
            return

        print(f"  - Upsert {model_name}: '{db_obj.title}'.")
        try:
            metadata = {
                "story_id": str(story_id),
                "model_name": model_name,
                "title": db_obj.title,
            }

            text_to_index = getattr(db_obj, 'description', getattr(db_obj, 'overview', ''))
            if not text_to_index:
                print(f"  - Skipping indexing for {model_name} '{db_obj.title}' due to empty content.")
                return

            super().upsert_document(
                doc_id=str(db_obj.id), text=text_to_index, metadata=metadata
            )

            print(f"  - Indexed {model_name} '{db_obj.title}' in vector store.")
        except Exception as e:
            print(f"  - Failed to index {model_name} '{db_obj.title}': {e}")

comic_vector_store_service = ComicVectorStoreService()