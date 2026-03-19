import os
from pydantic_settings import BaseSettings
from pydantic import Field

class DBSettings(BaseSettings):
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_PORT: int = Field(5432, env="DB_PORT")
    ECHO: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class Neo4jSettings(BaseSettings):
    NEO4J_URI: str = Field(..., env="NEO4J_URI")
    NEO4J_USER: str = Field(..., env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")

class Settings(BaseSettings):
    # --- General Settings ---
    PROJECT_NAME: str = "Wizdom Analyzer Service"

    # --- Database Settings ---
    db: DBSettings = DBSettings()
    neo4j: Neo4jSettings = Neo4jSettings()

    # --- Google API Key ---
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")

    # --- Google API AI Model Version  ---
    google_ai_model_version: str = Field(..., env="GOOGLE_AI_MODEL_VERSION")

    # --- Redis URL ---
    REDIS_URL: str = Field(..., env="REDIS_URL")

settings = Settings()
