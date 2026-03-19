
import os
from typing import Optional
import chromadb
from chromadb.api.client import Client
from chromadb.config import Settings

_client: Optional[Client] = None

def get_vector_store_client() -> Client:
    """
    Returns a ChromaDB client, initializing it if necessary.
    The client is configured via environment variables.
    """
    global _client
    if _client is None:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        
        print(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}")
        
        try:
            _client = chromadb.HttpClient(
                host=chroma_host,
                port=int(chroma_port),
                settings=Settings(anonymized_telemetry=False)
            )
            # You can add a check here to see if the server is alive
            _client.heartbeat() 
            print("Successfully connected to ChromaDB.")
        except Exception as e:
            print(f"Failed to initialize ChromaDB client: {e}")
            raise
            
    return _client
