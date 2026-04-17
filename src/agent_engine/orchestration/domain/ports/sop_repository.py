from abc import ABC, abstractmethod
from agent_engine.orchestration.domain.value_objects.sop_content import SopContent


class SopRepository(ABC):
    """SOP 仓储，根据 scope_level 和 architecture_layer 加载对应的操作规程"""

    @abstractmethod
    async def get_sop(self, scope_level: str, architecture_layer: str | None = None) -> SopContent: ...
