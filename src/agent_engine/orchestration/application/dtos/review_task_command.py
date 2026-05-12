from pydantic import BaseModel, Field


class ReviewTaskCommand(BaseModel):
    """审核任务指令"""

    task_id: str
    parent_id: str | None = Field(default=None)
