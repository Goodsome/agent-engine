from agent_engine.shared.domain.core.value_object import ValueObject
from agent_engine.dispatching.domain.enums import DispatchStatus

class ExecutionReceipt(ValueObject):
    """执行回执：Dispatching 上下文执行后的产物"""
    status: DispatchStatus
    output: str | None = None
    fault: str | None = None
