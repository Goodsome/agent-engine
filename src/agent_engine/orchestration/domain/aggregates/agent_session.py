from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.shared.models import Aggregate
from pydantic import Field
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId


class AgentSession(Aggregate):
    """聚合根 — 一次完整的 Agent 运行生命周期，包括 Prompt 组装、工具挂载和最终输出。"""

    id: SessionId
    job_id: JobId
    context_payload: dict
    status: SessionStatus
    final_output: str | None = Field(default=None)
    error_message: str | None = Field(default=None)

    def start(self) -> None:
        self.status = SessionStatus.RUNNING

    def finish_with_success(self, output: str) -> None:
        self.status = SessionStatus.SUCCESS
        self.final_output = output

    def finish_with_error(self, error: str) -> None:
        self.status = SessionStatus.ERROR
        self.error_message = error
