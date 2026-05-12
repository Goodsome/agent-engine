from pydantic import BaseModel, Field


class DispatchTaskResult(BaseModel):
    """调度任务结果 DTO"""

    session_id: str
    status: str
    output: str | None = Field(default=None)
    fault: str | None = Field(default=None)
