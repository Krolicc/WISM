from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# This builds a robust path to the .env file, which is located in the project root
# Path(__file__) -> .../backend/app/core/config.py
# .parent        -> .../backend/app/core/
# .parent        -> .../backend/app/
# .parent        -> .../backend/
# .parent        -> .../ (project root)
env_path = Path(__file__).parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    """Manages application settings and secrets."""
    google_api_key: str

    # Load settings from the explicitly defined .env file path
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8')

# Create a single settings instance to be used throughout the app
settings = Settings()
