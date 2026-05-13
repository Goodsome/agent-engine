from tests.integration.dispatching.application.use_cases.execute_session.bindings_execute import (
    ExecuteBindings,
    execute_bindings,
)

_ = execute_bindings


def test_使用有效_project_id_获取工作目录(execute_bindings: ExecuteBindings) -> None:
    execute_bindings.given(
        "ExecuteSession 依赖一个 WorkspaceManager 实例"
    ).arrange_done().when("执行包含有效 project_id 的 ExecuteSessionCommand").then(
        "应通过 WorkspaceManager 解析工作目录，而非硬编码路径"
    )


def test_project_id_为空时工作目录为_none(execute_bindings: ExecuteBindings) -> None:
    execute_bindings.given(
        "ExecuteSession 依赖一个 WorkspaceManager 实例"
    ).arrange_done().when("执行 project_id 为空的 ExecuteSessionCommand").then(
        "工作目录应为 None，不调用 WorkspaceManager"
    )


def test_workspace_manager_抛出异常时向上传播(
    execute_bindings: ExecuteBindings,
) -> None:
    execute_bindings.given(
        "WorkspaceManager 对某个 project_id 抛出 ProjectNotFound 异常"
    ).arrange_done().when("执行包含该 project_id 的 ExecuteSessionCommand").then(
        "异常应向上传播，不被 ExecuteSession 吞没"
    )
