from pydantic import BaseModel, Field


class DispatchTaskCommand(BaseModel):
    """调度任务指令：描述了要由哪个 Agent 执行哪个任务"""

    task_id: str
    project_id: str
    scope_level: str
    architecture_layer: str | None = Field(default=None)
    context_payload: dict[str, str | None] = Field(default_factory=dict)
