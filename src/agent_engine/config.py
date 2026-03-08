from pathlib import Path
import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Set up global configuration path for CLI usage across different projects
GLOBAL_CONFIG_DIR = Path.home() / ".agent-engine"
GLOBAL_ENV_FILE = GLOBAL_CONFIG_DIR / ".env"
LOCAL_ENV_FILE = Path.cwd() / ".env"

class Settings(BaseSettings):
    """
    Application settings using pydantic-settings.
    Loads configuration from environment variables and .env files.
    """
    # Database Configuration
    DATABASE_URL: PostgresDsn | None = Field(
        default=None,
        description="PostgreSQL Database Connection String"
    )
    
    TASK_GRAPH_DATABASE_URL: PostgresDsn | None = Field(
        default=None,
        description="PostgreSQL Task Graph Database Connection String"
    )

    # Agent Configuration
    AGENT_PROVIDER: str = Field(
        default="gemini",
        description="The agent provider to use (claude or gemini)"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Event Bus Configuration
    EVENT_BUS_CHANNEL: str = Field(
        default="domain_events",
        description="PostgreSQL NOTIFY channel for domain events"
    )
    
    # General Configuration
    PROJECT_ROOT: str = Field(
        default=".",
        description="Root directory of the project"
    )

    model_config = SettingsConfigDict(
        # Load global first, then allow local .env to override
        env_file=(GLOBAL_ENV_FILE, LOCAL_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unexpected environment variables
    )

_settings: Settings | None = None

def get_settings() -> Settings:
    """Singleton getter for settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
