from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.services.providers.vector_store_service import VectorStoreService

router = APIRouter()

# Provider function for the service
def get_vector_store_service() -> VectorStoreService:
    """Instantiates and returns the vector store service."""
    return VectorStoreService()

@router.get("/", response_model=Dict[str, Any])
def read_all_vectors(
    vector_store_service: VectorStoreService = Depends(get_vector_store_service),
):
    """
    Retrieve all vectors.
    """
    return vector_store_service.get_all_vectors()
