from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Manages application settings and secrets."""
    groq_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


# Create a single, reusable instance of the settings
settings = Settings()
