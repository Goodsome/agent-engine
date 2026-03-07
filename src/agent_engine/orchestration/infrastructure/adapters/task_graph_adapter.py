from agent_engine.orchestration.domain.value_objects.ready_task_dto import ReadyTaskDTO
from agent_engine.orchestration.domain.ports.task_graph_query_port import (
    TaskGraphQueryPort,
)
from dataclasses import dataclass


@dataclass
class TaskGraphAdapter(TaskGraphQueryPort):
    """通过 TaskGraph 服务获取 Ready 任务"""

    async def fetch_ready_tasks(self) -> list[ReadyTaskDTO]:
        # Mocked API call
        return []
