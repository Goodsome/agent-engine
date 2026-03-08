from dataclasses import dataclass
from typing import Optional
from agent_engine.execution.domain.enums import ModelTier

@dataclass
class SopContent:
    system_prompt: str
    model_tier: Optional[ModelTier] = None
