from pydantic import BaseModel, Field


class ReviewTaskQuery(BaseModel):
    task_id: str
    parent_id: str | None = Field(default=None)
