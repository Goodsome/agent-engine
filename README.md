# AgentEngine

AgentEngine 是一个事件驱动的 AI Agent 编排执行系统。它订阅 [TaskGraph](../task-graph) 发布的任务领域事件（Redis Streams），按任务层级匹配 SOP 执行规程，派发 Claude Agent 会话执行；执行结果由 Agent 依据 SOP 约定通过 TaskGraph 的 MCP 工具回写，形成"规划 — 派发 — 执行 — 验收"闭环。

## 🏛️ 架构概览

系统遵循领域驱动设计（DDD），由依赖注入组合根（`dependency-injector`）装配四个限界上下文：

| 上下文 | 职责 |
| --- | --- |
| `orchestration` | 事件订阅与任务派发：`OnTaskReady` / `OnTaskReviewRequested` / `OnTaskChangesRequested` 事件处理器，`DispatchTask` 用例，`AgentSession` 聚合 |
| `dispatching` | Agent 会话执行：`ExecuteSession` 用例 + `AgentExecutorPort` 端口及 `ClaudeAgentExecutorAdapter` 适配器（官方 Claude Agent SDK，流式响应） |
| `agent_registry` | SOP 执行规程与 Agent Profile 加载（`agent_registry/sops/`） |
| `integration` | 飞书 / Lark 集成（WebSocket 机器人触发会话） |

## 🧩 核心设计

### 事件总线
跨进程事件经独立的 [event-hub](../event-hub) 包走 **Redis Streams**（`XREADGROUP` 消费组，按聚合实体分主题保证单聚合内有序）。事件链路：TaskGraph 聚合记录领域事件 → UnitOfWork 提交后发布 → 转集成事件 XADD → AgentEngine 长驻监听（`agent-engine listen`）触发派发。

### SOP 执行规程体系
SOP 以 Markdown + YAML Frontmatter 定义于 `src/agent_engine/agent_registry/sops/`，按四层角色组织（`project` / `context` / `architecture` / `component`，另有分层规则文件与 TVD 工作流）。派发时按任务的 `scope_level` 与架构层动态组装系统提示词并注入对应规则——**提示词是任务元数据的函数**。

### 会话续接
`ClaudeAgentExecutorAdapter` 通过 `get_session_info()` 探测已有会话，决定 resume 还是新开，并继承先前会话的工作目录——Review / Revise 类操作可以在新的进程里**续接同一条 Claude 对话**，保留原任务上下文。

## 🚀 快速开始

```bash
uv sync                          # 同步依赖
uv run pytest                    # 运行测试
uv run basedpyright              # 类型检查

uv run agent-engine listen                   # 长驻事件监听（需 Redis）
uv run agent-engine execute-session --help
```

## ⚙️ 配置

通过环境变量配置（`~/.agent-engine/.env` 或项目根 `.env`）：`DATABASE_URL`（PostgreSQL）、Redis 地址、Agent 供应商等，见 `bootstrap/config.py`。
