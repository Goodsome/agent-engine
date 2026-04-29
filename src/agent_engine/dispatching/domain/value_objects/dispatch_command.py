from typing import Any
from pydantic import Field
from agent_engine.shared.models import ValueObject
from agent_engine.shared.domain.enums import ModelTier

class DispatchCommand(ValueObject):
    """派发指令：包含执行 Agent 所需的所有不可变数据"""
    system_prompt: str
    user_prompt: str
    session_id: str
    model_tier: ModelTier | None = None
    tools: list[str] = Field(default_factory=lambda: ["Read", "Edit", "Glob"])
    context_payload: dict[str, Any] = Field(default_factory=dict)
