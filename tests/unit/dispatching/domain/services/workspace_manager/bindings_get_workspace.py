from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import pytest

from agent_engine.dispatching.domain.exceptions.project_not_found import (
    ProjectNotFound,
)
from agent_engine.dispatching.domain.services.workspace_manager import WorkspaceManager
from agent_engine.shared.domain.value_objects.project_id import ProjectId


@dataclass
class GetWorkspaceBindings:
    root_dir: Path
    _last_step_type: str | None = None
    _manager: WorkspaceManager | None = None
    _project_id: ProjectId | None = None
    _result: Path | None = None
    _raised_exception: Exception | None = field(default=None, repr=False)

    # ── Given ──────────────────────────────────────────────────────

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case '系统中存在一个 ProjectId 为 "agent-engine" 的项目':
                self._setup_existing_project("agent-engine")
            case '系统中不存在 ProjectId 为 "nonexistent-project" 的项目':
                self._setup_nonexistent_project("nonexistent-project")
            case "系统中存在任意有效项目":
                self._setup_existing_project("sample-project")
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    # ── When ───────────────────────────────────────────────────────

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "WorkspaceManager 使用该 ProjectId 获取工作目录":
                self._act_get_workspace()
            case "WorkspaceManager 获取该项目的工作目录":
                self._act_get_workspace()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    # ── Then ───────────────────────────────────────────────────────

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "应返回该项目对应的文件系统路径（Path 类型）":
                self._assert_returns_path()
            case "应抛出 ProjectNotFound 异常":
                self._assert_raises_project_not_found()
            case "返回的路径应为绝对路径且可访问":
                self._assert_path_is_absolute_and_accessible()
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

    def _setup_existing_project(self: Self, project_name: str) -> None:
        project_dir = self.root_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        self._project_id = ProjectId(value=project_name)
        self._manager = WorkspaceManager(root_dir=self.root_dir)

    def _setup_nonexistent_project(self: Self, project_name: str) -> None:
        self._project_id = ProjectId(value=project_name)
        self._manager = WorkspaceManager(root_dir=self.root_dir)

    # ── Private: Act ───────────────────────────────────────────────

    def _act_get_workspace(self: Self) -> None:
        assert self._manager is not None
        assert self._project_id is not None
        try:
            self._result = self._manager.get_workspace(self._project_id)
            self._raised_exception = None
        except ProjectNotFound as exc:
            self._raised_exception = exc
            self._result = None

    # ── Private: Assert ────────────────────────────────────────────

    def _assert_returns_path(self: Self) -> None:
        assert self._result is not None, "Expected a Path, got None"
        assert isinstance(self._result, Path), (
            f"Expected Path, got {type(self._result).__name__}"
        )
        assert self._project_id is not None
        expected = self.root_dir / self._project_id.value
        assert self._result == expected, f"Expected {expected}, got {self._result}"

    def _assert_raises_project_not_found(self: Self) -> None:
        assert isinstance(self._raised_exception, ProjectNotFound), (
            f"Expected ProjectNotFound, got {type(self._raised_exception).__name__}"
        )
        assert self._project_id is not None
        assert self._raised_exception.project_id == self._project_id.value

    def _assert_path_is_absolute_and_accessible(self: Self) -> None:
        assert self._result is not None, "Expected a Path, got None"
        assert self._result.is_absolute(), f"Expected absolute path, got {self._result}"
        assert self._result.exists(), (
            f"Expected accessible path, but {self._result} does not exist"
        )


@pytest.fixture
def get_workspace_bindings(tmp_path: Path) -> GetWorkspaceBindings:
    return GetWorkspaceBindings(root_dir=tmp_path)
