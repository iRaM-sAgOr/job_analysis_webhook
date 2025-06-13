"""
Application configuration management using Pydantic Settings.
Handles environment variables, API keys, and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    PROJECT_NAME: str = "Job Analysis Webhook Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Security settings
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]

    # LLM Provider settings
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_MODEL: Optional[str] = None
    LLM_PROVIDER: Optional[str] = "gemini"  # Options: "openai", "gemini", "anthropic"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: Optional[str] = "gemini-1.5-flash"

    # Webhook settings
    WEBHOOK_SECRET: Optional[str] = None
    MAX_PAYLOAD_SIZE: int = 1024 * 1024  # 1MB

    # Additional settings
    API_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
