from __future__ import annotations

import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from typing import Self
from unittest.mock import AsyncMock, MagicMock

import pytest

from agent_engine.dispatching.application.dtos.execute_session_command import (
    ExecuteSessionCommand,
)
from agent_engine.dispatching.application.dtos.execute_session_result import (
    ExecuteSessionResult,
)
from agent_engine.dispatching.application.use_cases.execute_session import (
    ExecuteSession,
)
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.dispatching.domain.exceptions.project_not_found import (
    ProjectNotFound,
)
from agent_engine.dispatching.domain.ports.agent_executor_port import AgentExecutorPort
from agent_engine.dispatching.domain.services.workspace_manager import WorkspaceManager
from agent_engine.dispatching.domain.value_objects.execution_receipt import (
    ExecutionReceipt,
)
from agent_engine.shared.domain.value_objects.project_id import ProjectId


@dataclass
class ExecuteBindings:
    _last_step_type: str | None = None
    _executor: AgentExecutorPort | None = field(default=None, repr=False)
    _workspace_manager: WorkspaceManager | None = field(default=None, repr=False)
    _use_case: ExecuteSession | None = None
    _command: ExecuteSessionCommand | None = None
    _result: ExecuteSessionResult | None = None
    _raised_exception: Exception | None = field(default=None, repr=False)

    # ── Given ──────────────────────────────────────────────────────

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case "ExecuteSession 依赖一个 WorkspaceManager 实例":
                self._setup_with_mock_workspace_manager()
            case "WorkspaceManager 对某个 project_id 抛出 ProjectNotFound 异常":
                self._setup_with_failing_workspace_manager()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    # ── When ───────────────────────────────────────────────────────

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "执行包含有效 project_id 的 ExecuteSessionCommand":
                self._act_execute_with_valid_project_id()
            case "执行 project_id 为空的 ExecuteSessionCommand":
                self._act_execute_with_empty_project_id()
            case "执行包含该 project_id 的 ExecuteSessionCommand":
                self._act_execute_with_failing_project_id()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    # ── Then ───────────────────────────────────────────────────────

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "应通过 WorkspaceManager 解析工作目录，而非硬编码路径":
                self._assert_workspace_manager_resolved_cwd()
            case "工作目录应为 None，不调用 WorkspaceManager":
                self._assert_workspace_manager_not_called()
            case "异常应向上传播，不被 ExecuteSession 吞没":
                self._assert_project_not_found_propagated()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    def and_(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    def but(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    # ── Private: Setup (Arrange) ───────────────────────────────────

    def _setup_with_mock_workspace_manager(self: Self) -> None:
        """构造 ExecuteSession 实例，含 mock 的 AgentExecutorPort 和 WorkspaceManager。"""
        self._executor = MagicMock(spec=AgentExecutorPort)
        self._executor.execute = AsyncMock(
            return_value=ExecutionReceipt(
                status=DispatchStatus.SUCCESS, output="ok", fault=None
            )
        )
        self._workspace_manager = MagicMock(spec=WorkspaceManager)
        self._use_case = ExecuteSession(
            executor=self._executor,
            workspace_manager=self._workspace_manager,
        )

    def _setup_with_failing_workspace_manager(self: Self) -> None:
        """构造 WorkspaceManager，对特定 project_id 抛出 ProjectNotFound。"""
        self._executor = MagicMock(spec=AgentExecutorPort)
        self._executor.execute = AsyncMock(
            return_value=ExecutionReceipt(
                status=DispatchStatus.SUCCESS, output="ok", fault=None
            )
        )
        self._workspace_manager = MagicMock(spec=WorkspaceManager)
        self._workspace_manager.get_workspace.side_effect = ProjectNotFound(
            "failing-project", root=Path("/tmp")
        )
        self._use_case = ExecuteSession(
            executor=self._executor,
            workspace_manager=self._workspace_manager,
        )

    # ── Private: Act ───────────────────────────────────────────────

    def _act_execute_with_valid_project_id(self: Self) -> None:
        """构造包含有效 project_id 的命令并执行。"""
        assert self._use_case is not None
        self._command = ExecuteSessionCommand(
            system_prompt="test system prompt",
            user_prompt="test user prompt",
            session_id="session-001",
            project_id="my-project",
        )
        try:
            self._result = asyncio.run(self._use_case.execute(self._command))
            self._raised_exception = None
        except Exception as exc:
            self._raised_exception = exc
            self._result = None

    def _act_execute_with_empty_project_id(self: Self) -> None:
        """构造 project_id 为空的命令并执行。"""
        assert self._use_case is not None
        self._command = ExecuteSessionCommand(
            system_prompt="test system prompt",
            user_prompt="test user prompt",
            session_id="session-002",
            project_id="",
        )
        try:
            self._result = asyncio.run(self._use_case.execute(self._command))
            self._raised_exception = None
        except Exception as exc:
            self._raised_exception = exc
            self._result = None

    def _act_execute_with_failing_project_id(self: Self) -> None:
        """构造包含会触发 ProjectNotFound 的 project_id 的命令并执行。"""
        assert self._use_case is not None
        self._command = ExecuteSessionCommand(
            system_prompt="test system prompt",
            user_prompt="test user prompt",
            session_id="session-003",
            project_id="failing-project",
        )
        try:
            self._result = asyncio.run(self._use_case.execute(self._command))
            self._raised_exception = None
        except ProjectNotFound as exc:
            self._raised_exception = exc
            self._result = None

    # ── Private: Assert ────────────────────────────────────────────

    def _assert_workspace_manager_resolved_cwd(self: Self) -> None:
        """断言 WorkspaceManager.get_workspace 被调用，且执行器接收了正确 cwd。"""
        assert self._workspace_manager is not None
        assert self._command is not None
        assert self._executor is not None

        self._workspace_manager.get_workspace.assert_called_once_with(
            ProjectId(value=self._command.project_id)
        )
        expected_cwd = self._workspace_manager.get_workspace.return_value
        self._executor.execute.assert_called_once()
        call_kwargs = self._executor.execute.call_args.kwargs
        assert call_kwargs["cwd"] == expected_cwd, (
            f"Expected cwd={expected_cwd}, got {call_kwargs['cwd']}"
        )
        assert self._result is not None
        assert isinstance(self._result, ExecuteSessionResult)
        assert self._result.status == DispatchStatus.SUCCESS

    def _assert_workspace_manager_not_called(self: Self) -> None:
        """断言 WorkspaceManager.get_workspace 未被调用，cwd 为 None。"""
        assert self._workspace_manager is not None
        assert self._executor is not None

        self._workspace_manager.get_workspace.assert_not_called()
        self._executor.execute.assert_called_once()
        call_kwargs = self._executor.execute.call_args.kwargs
        assert call_kwargs["cwd"] is None, (
            f"Expected cwd=None, got {call_kwargs['cwd']}"
        )
        assert self._result is not None
        assert isinstance(self._result, ExecuteSessionResult)
        assert self._result.status == DispatchStatus.SUCCESS

    def _assert_project_not_found_propagated(self: Self) -> None:
        """断言 ProjectNotFound 异常向上传播。"""
        assert isinstance(self._raised_exception, ProjectNotFound), (
            f"Expected ProjectNotFound, got {type(self._raised_exception).__name__}"
        )
        assert self._raised_exception.project_id == "failing-project"


@pytest.fixture
def execute_bindings() -> ExecuteBindings:
    return ExecuteBindings()
