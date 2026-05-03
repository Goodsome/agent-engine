from abc import ABC, abstractmethod

from agent_engine.agent_registry.application.dtos.agent_profile import AgentProfile


class AgentProfileQueryService(ABC):
    @abstractmethod
    def get_profile(self, scope_level: str) -> AgentProfile:
        pass
