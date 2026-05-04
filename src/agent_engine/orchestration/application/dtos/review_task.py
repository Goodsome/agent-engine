from pydantic import BaseModel


class ReviewTaskCommand(BaseModel):
    """审核任务指令"""
    task_id: str
    parent_id: str | None = None


class ReviewTaskResult(BaseModel):
    """审核任务结果 DTO"""
    session_id: str | None = None
    status: str
    output: str | None = None
    fault: str | None = None
