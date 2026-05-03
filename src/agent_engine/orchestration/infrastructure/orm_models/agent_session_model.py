from typing import Any
from typing_extensions import override
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from agent_engine.shared.infrastructure.database import Base


class AgentSessionModel(Base):
    """Agent 会话的数据库模型，充分利用 PostgreSQL 特性"""

    __tablename__: str = "agent_sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    context_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    system_prompt: Mapped[str] = mapped_column(String, nullable=False, default="")
    messages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )

    __table_args__: Any = (
        # 再次确保 task_id 和 id (session_id) 的 1:1 关系（通过 unique=True 已经涵盖）
        # 这里主要利用 PostgreSQL 的索引特性
    )

    @override
    def __repr__(self) -> str:
        return f"AgentSessionModel(id={self.id}, task_id={self.task_id}, status={self.status})"
