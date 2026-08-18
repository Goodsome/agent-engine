from typing import Any
from agent_engine.shared.domain.enums import ModelTier
from pydantic import BaseModel, Field


class ExecuteSessionCommand(BaseModel):
    """执行会话指令：包含执行 Agent 所需的所有数据"""

    system_prompt: str
    user_prompt: str
    session_id: str
    project_id: str | None = Field(default=None)
    model_tier: ModelTier | None = Field(default=None)
    tools: list[str] = Field(default_factory=lambda: ["Read", "Edit", "Glob"])
    context_payload: dict[str, Any] = Field(default_factory=dict)
    context: str | None = Field(default=None)
