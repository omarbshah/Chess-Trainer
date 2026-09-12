from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    lichess_api_token: str = ""
    lichess_base_url: str = "https://lichess.org"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-flash"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, so the .env file is only read once per process."""
    return Settings()
