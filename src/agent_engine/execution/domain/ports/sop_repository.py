from abc import ABC, abstractmethod
from agent_engine.execution.domain.enums import SessionType


class SopRepository(ABC):
    """SOP 仓储，根据 SessionType 加载不同的操作规程"""

    @abstractmethod
    def get_sop(self, session_type: SessionType) -> str: ...
