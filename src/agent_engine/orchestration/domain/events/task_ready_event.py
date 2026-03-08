from pydantic import BaseModel
from agent_engine.shared.domain.value_objects.task_id import TaskId


class TaskReadyEvent(BaseModel):
    """
    领域事件：某个 Task 进入 Ready 状态，可以被调度执行。
    增加 project_id 字段，用于在多租户/多项目环境下仅处理当前相关任务。
    """
    event_type: str = "TaskReadyEvent"
    project_id: str
    task_id: TaskId
    planning_level: str
    status: str
    occurred_at: str
