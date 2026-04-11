"""
Bootstrap configuration for the entire application.
Loads project-level settings and merges context configurations.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Set up global configuration path for CLI usage across different projects
GLOBAL_CONFIG_DIR = Path.home() / ".agent-engine"
GLOBAL_ENV_FILE = GLOBAL_CONFIG_DIR / ".env"
LOCAL_ENV_FILE = Path.cwd() / ".env"


class AppConfig(BaseSettings):
    """
    Top-level application configuration.
    包含了 Project 级别的全局配置，并聚合了所有上下文的配置。
    """
    # Database Configuration
    DATABASE_URL: str | None = Field(
        default=None,
        description="PostgreSQL Database Connection String"
    )

    TASK_GRAPH_DATABASE_URL: str | None = Field(
        default=None,
        description="PostgreSQL Task Graph Database Connection String"
    )

    # Agent Configuration
    AGENT_PROVIDER: str = Field(
        default="claude",
        description="The agent provider to use (claude)"
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
    PROJECT_ID: str = Field(
        default="default",
        description="Identifier for the current project"
    )

    PROJECT_ROOT: str = Field(
        default=".",
        description="Root directory of the project"
    )

    # Feishu (Lark) Integration Configuration
    FEISHU_APP_ID: str | None = Field(
        default=None,
        description="Feishu App ID for bot integration"
    )

    FEISHU_APP_SECRET: str | None = Field(
        default=None,
        description="Feishu App Secret for bot integration"
    )

    model_config = SettingsConfigDict(
        # Load global first, then allow local .env to override
        env_file=(GLOBAL_ENV_FILE, LOCAL_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unexpected environment variables
    )


def load_all_configurations() -> AppConfig:
    """实例化全局配置（会自动触发各级环境变量的读取）"""
    return AppConfig()


__all__ = ["AppConfig", "load_all_configurations"]
