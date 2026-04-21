from dataclasses import dataclass
from typing import Optional
from agent_engine.shared.domain.enums import ModelTier

@dataclass(frozen=True)
class ExecutionBlueprint:
    """Agent 执行蓝图：包含系统提示词与执行参数（如模型档位）"""
    system_prompt: str
    model_tier: Optional[ModelTier] = None
