from abc import ABC, abstractmethod
from agent_engine.execution.domain.aggregates.agent_session import AgentSession

from src.agent_engine.shared.domain.value_objects.session_id import SessionId


class AgentSessionRepository(ABC):

    @abstractmethod
    def save(self, session: AgentSession) -> None: ...

    @abstractmethod
    def delete(self, agent_session_id: SessionId) -> None: ...

    @abstractmethod
    def find_by_id(self, agent_session_id: SessionId) -> AgentSession | None: ...
