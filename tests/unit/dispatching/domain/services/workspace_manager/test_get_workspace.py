from tests.unit.dispatching.domain.services.workspace_manager.bindings_get_workspace import (
    GetWorkspaceBindings,
    get_workspace_bindings,
)

_ = get_workspace_bindings


def test_获取已存在项目的工作目录(get_workspace_bindings: GetWorkspaceBindings) -> None:
    _ = (
        get_workspace_bindings.given(
            '系统中存在一个 ProjectId 为 "agent-engine" 的项目'
        )
        .arrange_done()
        .when("WorkspaceManager 使用该 ProjectId 获取工作目录")
        .then("应返回该项目对应的文件系统路径（Path 类型）")
    )


def test_获取不存在项目的工作目录(get_workspace_bindings: GetWorkspaceBindings) -> None:
    _ = (
        get_workspace_bindings.given(
            '系统中不存在 ProjectId 为 "nonexistent-project" 的项目'
        )
        .arrange_done()
        .when("WorkspaceManager 使用该 ProjectId 获取工作目录")
        .then("应抛出 ProjectNotFound 异常")
    )


def test_返回路径的有效性(get_workspace_bindings: GetWorkspaceBindings) -> None:
    _ = (
        get_workspace_bindings.given("系统中存在任意有效项目")
        .arrange_done()
        .when("WorkspaceManager 获取该项目的工作目录")
        .then("返回的路径应为绝对路径且可访问")
    )
