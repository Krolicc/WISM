import os
from pydantic_settings import BaseSettings
from pydantic import Field

# A new class to group all database-related settings
class DBSettings(BaseSettings):
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_PORT: int = Field(5432, env="DB_PORT")
    
    # SQLAlchemy logging, can be overridden by an env var if needed (e.g., DB_ECHO=true)
    ECHO: bool = False

    @property
    def url(self) -> str:
        """Constructs the SQLAlchemy database URL from settings."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Pydantic will automatically read from environment variables.
    # No need for the Config class if we rely on the env.

class Neo4jSettings(BaseSettings):
    NEO4J_URI: str = Field(..., env="NEO4J_URI")
    NEO4J_USER: str = Field(..., env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")

class Settings(BaseSettings):
    # --- General Settings ---
    PROJECT_NAME: str = "Comic Generator API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    # We now have a nested object for DB settings
    db: DBSettings = DBSettings()
    neo4j: Neo4jSettings = Neo4jSettings()

    # --- Google API Key ---
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")

    # --- Google API AI Model Version  ---
    google_ai_model_version: str = Field(..., env="GOOGLE_AI_MODEL_VERSION")

    # --- JWT Settings for FastAPI Users ---
    jwt_secret: str = Field(..., env="JWT_SECRET")

    # --- Redis URL ---
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # Pydantic will automatically read from environment variables.
    # No need for the Config class if we rely on the env.

settings = Settings()
