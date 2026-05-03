from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.shared.models import Aggregate
from pydantic import Field
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.project_id import ProjectId


class AgentSession(Aggregate):
    """聚合根 — 一次完整的 Agent 运行生命周期，包括 Prompt 组装、工具挂载和最终输出。"""

    id: SessionId
    project_id: ProjectId
    status: SessionStatus
    context_payload: dict[str, str]

    # messages: list[Message] = Field(default_factory=list)
