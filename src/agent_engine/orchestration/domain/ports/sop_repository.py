from abc import ABC, abstractmethod
from agent_engine.orchestration.domain.value_objects.sop_content import SopContent


class SopRepository(ABC):
    """SOP 仓储，根据 planning_level 和 status 加载对应的操作规程"""

    @abstractmethod
    async def get_sop(self, planning_level: str, status: str) -> SopContent: ...
