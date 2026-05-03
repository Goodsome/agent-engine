from pydantic import BaseModel, Field


class DispatchTaskCommand(BaseModel):
    """调度任务指令：描述了要由哪个 Agent 执行哪个任务"""
    task_id: str
    project_id: str
    scope_level: str
    context_payload: dict[str, str] = Field(default_factory=dict)


class DispatchTaskResult(BaseModel):
    """调度任务结果 DTO"""
    session_id: str
    status: str
    output: str | None = None
    fault: str | None = None
