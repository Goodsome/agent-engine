from typing import Any, Callable, NamedTuple, TypedDict
from agent_engine.execution.domain.aggregates.agent_session import AgentSession

TEST_CASES_START: list[StartCase] = []
TEST_CASES_FINISH_WITH_SUCCESS: list[FinishWithSuccessCase] = []
TEST_CASES_FINISH_WITH_ERROR: list[FinishWithErrorCase] = []


class StartCase(NamedTuple):
    instance: AgentSession
    expected: Any


class FinishWithSuccessCase(NamedTuple):
    instance: AgentSession
    output: str
    expected: Any


class FinishWithErrorCase(NamedTuple):
    instance: AgentSession
    error: str
    expected: Any
