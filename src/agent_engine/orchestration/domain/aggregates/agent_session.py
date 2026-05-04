from pydantic import Field
from agent_engine.shared.models import Aggregate
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.project_id import ProjectId
from agent_engine.shared.domain.value_objects.task_id import TaskId

from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.orchestration.domain.value_objects.message import Message



class AgentSession(Aggregate):
    """聚合根 — 一次完整的 Agent 运行生命周期，包括 Prompt 组装、工具挂载和最终输出。"""

    id: SessionId
    task_id: TaskId
    project_id: ProjectId
    status: SessionStatus
    context_payload: dict[str, str | None]

    system_prompt: str = ""
    messages: list[Message] = Field(default_factory=list)
