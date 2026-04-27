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

class Settings(BaseSettings):
    # --- General Settings ---
    PROJECT_NAME: str = "Comic Generator API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    # We now have a nested object for DB settings
    db: DBSettings = DBSettings()

    # --- Redis URL ---
    REDIS_URL: str = Field(..., env="REDIS_URL")

    COMFYUI_URL: str = Field(..., env="COMFYUI_URL")

    # Pydantic will automatically read from environment variables.
    # No need for the Config class if we rely on the env.

settings = Settings()
