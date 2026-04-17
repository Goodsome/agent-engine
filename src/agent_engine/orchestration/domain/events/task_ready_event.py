from pydantic import Field
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.enums import ScopeLevel, ArchitectureLayer
from agent_engine.shared.events import DomainEvent


class TaskReadyEvent(DomainEvent):
    """Event emitted when a task is ready to be claimed."""
    task_id: TaskId = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    bounded_context: str | None = Field(default=None, description="Bounded context the task belongs to")
    architecture_layer: ArchitectureLayer | None = Field(default=None, description="DDD architecture layer the task targets")
