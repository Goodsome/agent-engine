from pydantic import BaseModel, Field


class DispatchTaskQuery(BaseModel):
    task_id: str
    project_id: str
    scope_level: str
    architecture_layer: str | None = Field(default=None)
    context_payload: dict[str, str | None] = Field(default_factory=dict)
