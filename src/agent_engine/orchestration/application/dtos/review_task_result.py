from pydantic import BaseModel, Field


class ReviewTaskResult(BaseModel):
    """审核任务结果 DTO"""

    session_id: str | None = Field(default=None)
    status: str
    output: str | None = Field(default=None)
    fault: str | None = Field(default=None)
