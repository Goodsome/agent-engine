from typing import Any, Callable, NamedTuple, TypedDict
import os
import tempfile
import pytest

class GetSopCase(NamedTuple):
    mocks_setup: Callable
    planning_level: str
    status: str
    expected: Any

def _setup_mocks_success():
    pass

# We can't easily mock `frontmatter.load` inside `cases_*.py` if we want real file reading test.
# However, for unit testing the adapter, we can mock `frontmatter.load`.
# For a more robust test, we might use a real file if `LocalFileSopRepository` points to a temp directory.

TEST_CASES_GET_SOP: list[GetSopCase] = [
    GetSopCase(
        mocks_setup=_setup_mocks_success,
        planning_level="story",
        status="ready",
        expected=lambda result: "Name: story_planner" in result.system_prompt and "Decomposition & Planning" in result.system_prompt and "规划流程与执行指南" in result.system_prompt
    ),
    GetSopCase(
        mocks_setup=_setup_mocks_success,
        planning_level="architecture",
        status="review",
        expected=lambda result: "Name: architecture_reviewer" in result.system_prompt and "审查 T1 架构决策文档" in result.system_prompt and "🧭 执行指引 (Guidance)" in result.system_prompt
    )
]
