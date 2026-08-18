# AgentEngine

AgentEngine 是一个事件驱动的 AI Agent 编排执行系统。它消费 [TaskGraph](../task-graph) 发出的任务就绪领域事件（PostgreSQL LISTEN/NOTIFY），自动派发给 Claude Agent 会话执行并回写结果，实现"规划 — 派发 — 执行 — 验收"的任务闭环。

## 🏛️ 架构概览

系统遵循领域驱动设计（DDD），按限界上下文拆分为两个独立容器：

**1. Orchestration Context（编排上下文）**
- 管理任务派发与 DispatchJob 生命周期
- 处理领域事件：`TaskReadyEvent`、`TaskReviewRequestedEvent`
- 核心用例：`HandleDispatchableTaskEvent`

**2. Execution Context（执行上下文）**
- 通过 `ClaudeAgentGateway` 管理 AI Agent 会话
- 聚合根：`AgentSession`
- 核心用例：`ExecuteAgentSession`

## 🧩 核心设计

### 事件驱动通信
领域事件通过 PostgreSQL NOTIFY 广播，`PgNotifyEventListener` 长驻监听指定频道，收到事件后触发对应派发用例，从而解耦规划（TaskGraph）与执行（AgentEngine）两个系统。

### SOP 标准作业流程体系
SOP 以 Markdown + YAML Frontmatter 形式定义于 `src/agent_engine/sops/`：

- 命名约定：`{planning_level}_{status}.md`（如 `atomic_ready.md`）
- Frontmatter 声明：`name`、`description`、`tools`、`model`（fast/pro 分级）
- 运行时由 `LocalFileSopRepository` 加载并动态组装为 Agent 系统提示词，让不同层级的任务自动匹配不同成本的执行策略

### Port/Adapter 模式
- 端口定义于 `domain/ports/`（如 `AgentGateway`）
- 适配器实现于 `infrastructure/adapters/`（如 `ClaudeAgentGateway`），隔离 LLM 供应商细节
- `dependency-injector` 组合根统一装配双上下文容器

## 🚀 快速开始

本项目依赖 `uv` 作为包与环境管理工具：

```bash
uv sync                 # 同步依赖并创建虚拟环境
uv run pytest           # 运行测试
uv run basedpyright     # 类型检查

uv run agent-engine listen              # 启动长驻事件监听
uv run agent-engine execute-session --help
```

## ⚙️ 配置

通过环境变量配置（加载自 `~/.agent-engine/.env` 或项目根目录 `.env`）：

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | AgentEngine 自身 PostgreSQL 连接串 |
| `TASK_GRAPH_DATABASE_URL` | TaskGraph PostgreSQL 连接串 |
| `AGENT_PROVIDER` | Agent 供应商（默认 `claude`） |
| `EVENT_BUS_CHANNEL` | PostgreSQL NOTIFY 频道（默认 `domain_events`） |
| `PROJECT_ID` / `PROJECT_ROOT` | 当前项目标识与根目录 |
