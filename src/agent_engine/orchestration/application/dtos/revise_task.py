from pydantic import BaseModel


class ReviseTaskCommand(BaseModel):
    """重新修改任务指令"""
    task_id: str


class ReviseTaskResult(BaseModel):
    """重新修改任务结果 DTO"""
    session_id: str | None = None
    status: str
    output: str | None = None
    fault: str | None = None
