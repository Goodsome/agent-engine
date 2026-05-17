from typing import Any
from pydantic import model_serializer, model_validator
from agent_engine.shared.domain.core.value_object import ValueObject


class ProjectId(ValueObject):
    """项目唯一标识"""

    value: str

    def __str__(self) -> str:
        return self.value

    @model_serializer
    def serialize(self) -> str:
        return self.value

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"value": data}
        return data
    