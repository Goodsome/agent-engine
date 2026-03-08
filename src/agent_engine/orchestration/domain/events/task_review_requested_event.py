from typing import Literal

from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.enums import PlanningLevel, TaskStatus
from agent_engine.shared.events import DomainEvent


class TaskReviewRequestedEvent(DomainEvent):
    """
    领域事件：某个 Task 进入 Review 状态，需要被调度进行代码审查或验收。
    增加 project_id 字段，用于在多租户/多项目环境下仅处理当前相关任务。
    """
    project_id: str
    task_id: TaskId
    planning_level: PlanningLevel
    status: Literal[TaskStatus.REVIEW] = TaskStatus.REVIEW
