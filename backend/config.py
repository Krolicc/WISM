from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# This builds a robust path to the .env file, which is located in the project root
# (one level up from the 'backend' directory where this config.py file is).
# Path(__file__) -> .../backend/config.py
# .parent        -> .../backend/
# .parent        -> .../ (project root)
# / ".env"       -> .../.env
env_path = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    """Manages application settings and secrets."""
    google_api_key: str

    # Load settings from the explicitly defined .env file path
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8')

# Create a single settings instance to be used throughout the app
settings = Settings()
