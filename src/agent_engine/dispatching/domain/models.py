from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
from agent_engine.shared.domain.enums import ModelTier

class DispatchStatus(Enum):
    SUCCESS = "success"
    FAULT = "fault"

@dataclass(frozen=True)
class DispatchCommand:
    """派发指令：包含执行 Agent 所需的所有不可变数据"""
    system_prompt: str
    user_prompt: str
    session_id: str
    model_tier: Optional[ModelTier] = None
    tools: list[str] = field(default_factory=lambda: ["Read", "Edit", "Glob"])
    context_payload: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ExecutionReceipt:
    """执行回执：Dispatching 上下文执行后的产物"""
    status: DispatchStatus
    output: Optional[str] = None
    fault: Optional[str] = None
