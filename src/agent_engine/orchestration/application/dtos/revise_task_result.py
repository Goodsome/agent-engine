from pydantic import BaseModel, Field


class ReviseTaskResult(BaseModel):
    """重新修改任务结果 DTO"""

    session_id: str | None = Field(default=None)
    status: str
    output: str | None = Field(default=None)
    fault: str | None = Field(default=None)
