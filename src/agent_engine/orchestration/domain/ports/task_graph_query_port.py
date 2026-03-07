from agent_engine.orchestration.domain.value_objects.ready_task_dto import ReadyTaskDTO
from abc import ABC, abstractmethod


class TaskGraphQueryPort(ABC):
    """防腐层：读取 TaskGraph 状态的只读接口，未来可替换为事件订阅(Pub/Sub)客户端。"""

    @abstractmethod
    async def fetch_ready_tasks(self) -> list[ReadyTaskDTO]: ...
