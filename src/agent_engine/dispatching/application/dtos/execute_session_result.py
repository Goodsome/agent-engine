from pydantic import BaseModel, Field
from agent_engine.dispatching.domain.enums import DispatchStatus


class ExecuteSessionResult(BaseModel):
    """执行会话结果 DTO"""

    status: DispatchStatus
    output: str | None = Field(default=None)
    fault: str | None = Field(default=None)
