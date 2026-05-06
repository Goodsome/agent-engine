from agent_engine.shared.domain.core.value_object import ValueObject
from uuid import UUID, uuid4
from pydantic import model_serializer, model_validator
from typing import Any


class JobId(ValueObject):
    """调度派发任务的唯一标识"""

    value: UUID

    @classmethod
    def create(cls):
        return cls(value=uuid4())
    
    @classmethod
    def reconstitute(cls, value: UUID | str):
        if isinstance(value, str):
            value = UUID(value)
        return cls(value=value)
    
    def __str__(self):
        return str(self.value)

    @model_serializer
    def serialize(self) -> str:
        return str(self.value)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, (str, UUID)):
            return {"value": data}
        return data
