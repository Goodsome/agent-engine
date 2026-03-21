# Orchestration 上下文 - DDD 战略设计文档

## 1. 上下文命名与核心愿景

### 1.1 上下文名称

**Orchestration**（编排上下文）

### 1.2 核心职责

Orchestration 上下文负责 AI Agent 任务的调度编排，包括监听任务就绪事件、加载操作规程（SOP）、创建分发任务记录、触发 Execution 上下文执行，并维护任务执行的生命周期状态。

### 1.3 问题陈述

在 Agent 编排系统中，需要一个专门的边界来协调"何时何地"执行任务。这个边界需要解决以下痛点：

1. **任务触发协调**：外部系统（TaskGraph）通过 PostgreSQL NOTIFY 发布任务状态变更，需要有专门的监听机制捕获 TaskReadyEvent 和 TaskReviewRequestedEvent
2. **操作规程管理**：不同 PlanningLevel（initiative/milestone/architectural/feature/atomic）的任务需要不同的 SOP 指导，需要根据任务特征动态加载对应的操作规程
3. **分发记录追踪**：每次任务分发需要生成 DispatchJob 记录，追踪从派发到完成（成功/失败）的完整过程
4. **跨上下文调用**：Orchestration 需要与 Execution 上下文协作，通过明确的端口（ExecutionTriggerPort）触发 Agent 执行

## 2. 统一语言词汇表

| 术语 | 英文别名 | 业务定义 |
|------|----------|----------|
| 调度任务 | Dispatch Job | 一次从 TaskGraph 拉取任务并尝试执行的分发记录，是 Orchestration 上下文的核心聚合根。 |
| 任务状态 | Task Status | TaskGraph 中任务的生命周期状态，包括：PENDING, BLOCKED, READY, IN_PROGRESS, REVIEW, DONE, CHANGES_REQUESTED, SKIPPED, DISCARDED。 |
| 规划级别 | Planning Level | 定义任务的不确定性和粒度层级，包括：INITIATIVE（初始）, MILESTONE（里程碑）, ARCHITECTURAL（架构级）, FEATURE（特性级）, ATOMIC（原子级）。 |
| 任务就绪事件 | Task Ready Event | 领域事件：当某个 Task 进入 READY 状态时可以触发调度执行。 |
| 任务审查请求事件 | Task Review Requested Event | 领域事件：当某个 Task 进入 REVIEW 状态时需要调度进行代码审查或验收。 |
| 操作规程 | SOP (Standard Operating Procedure) | 根据 planning_level 和 status 加载的操作指南文档，定义 Agent 执行时的系统提示词和行为规范。 |
| 执行触发端口 | Execution Trigger Port | 定义跨上下文调用端口，用于触发 Execution 上下文执行 Agent 会话。 |
| 任务查询端口 | Task Graph Query Port | 防腐层接口：读取 TaskGraph 状态的只读接口，未来可替换为事件订阅客户端。 |
| 事件监听端口 | Domain Event Listener Port | 端口：领域事件监听器，以异步迭代器形式持续产出事件。 |
| 任务图谱 | TaskGraph | 外部任务管理系统，维护项目任务的完整生命周期。 |
| 分发任务状态 | Job Status | DispatchJob 的生命周期状态，包括：PENDING, RUNNING, COMPLETED, FAILED。 |
| 会话标识 | Session Id | 关联到 Execution 上下文的 Agent Session 唯一标识。 |

## 3. 上下文映射与集成

### 3.1 协作关系

| 协作上下文 | 关系类型 | 说明 |
|------------|----------|------|
| **Execution** | 客户-供应商（Customer-Supplier） | Orchestration 是 Execution 的客户，通过 ExecutionTriggerPort 触发 Agent 执行。Orchestration 需要等待 Execution 返回结果以决定后续调度。 |
| **TaskGraph** | 外部系统 / 上游 | 外部任务管理系统，通过 PostgreSQL NOTIFY 发布任务状态变更事件。Orchestration 通过 TaskGraphQueryPort 主动拉取 Ready 任务。 |
| **Shared Kernel** | 共享内核 | 共享 TaskId、JobId、SessionId 等值对象，确保跨上下文的身份标识一致性。 |
| **Integration** | 下游消费者 | Integration 上下文（如飞书）可订阅 Orchestration 发布的事件，或使用相同的 ExecutionTriggerPort 触发执行。 |

### 3.2 集成模式

1. **发布/订阅（Pub/Sub）**：
   - Orchestration 通过 `PgNotifyEventListener` 订阅 PostgreSQL NOTIFY 通道
   - 监听 `TaskReadyEvent` 和 `TaskReviewRequestedEvent` 领域事件
   - 这种模式实现了任务触发与调度逻辑的解耦

2. **开放主机服务（OHS）**：
   - Orchestration 通过 `ExecutionTriggerPort` 向 Execution 上下文暴露执行能力
   - 该端口定义清晰的契约（JobId、System Prompt、Model Tier 等参数）
   - 实现为 `InProcessExecutionTrigger`，在进程内直接调用 Execution 上下文用例

3. **防腐层（ACL）**：
   - `TaskGraphQueryPort` 封装对外部 TaskGraph 系统的访问
   - `ReadyTaskDTO` 作为跨边界数据传输对象，屏蔽 TaskGraph 内部细节
   - 便于未来替换为事件订阅模式

4. **后续工作流起点**：
   - `StartInitialWorkflow` 支持 CLI 手动触发初始工作流
   - 用户输入自然语言需求，加载 `story` 级别 SOP，触发首轮 Agent 执行

### 3.3 上下文映射图

```mermaid
graph TB
    subgraph AgentEngine系统
        subgraph TaskGraph_External [TaskGraph (外部系统)]
            TG[(TaskGraph<br/>任务管理系统)]
            NOTIFY[PostgreSQL NOTIFY<br/>事件发布]
        end

        subgraph Orchestration_Context [Orchestration 上下文 - 本上下文]
            DJ[DispatchJob<br/>聚合根]
            UC1[HandleDispatchableTaskEvent<br/>用例]
            UC2[RunEventLoopTick<br/>用例]
            UC3[StartInitialWorkflow<br/>用例]
            ETP[ExecutionTriggerPort<br/>端口定义]
            TQP[TaskGraphQueryPort<br/>端口定义]
            DEL[DomainEventListenerPort<br/>端口定义]
            SOPR[SopRepository<br/>端口定义]
        end

        subgraph Execution_Context [Execution 上下文]
            AS[AgentSession<br/>聚合根]
            EAS[ExecuteAgentSession<br/>用例]
        end

        subgraph Shared_Kernel [Shared Kernel]
            VO1[TaskId<br/>值对象]
            VO2[JobId<br/>值对象]
            VO3[SessionId<br/>值对象]
        end

        subgraph Integration_Context [Integration 上下文]
            FEISHU[飞书集成]
        end

        subgraph Infrastructure [基础设施]
            PG[(PostgreSQL<br/>事件总线/持久化)]
            FS[(文件系统<br/>SOP 文件)]
        end
    end

    %% TaskGraph 发布事件
    TG -->|发布| NOTIFY
    NOTIFY -->|LISTEN| DEL

    %% 调度循环
    UC2 -->|拉取 Ready 任务| TQP
    TQP -.->|实现| TG
    UC2 --> SOPR
    SOPR -.->|实现| FS
    UC2 --> ETP
    UC1 --> ETP

    %% 触发执行
    ETP -.->|实现: InProcessExecutionTrigger| EAS

    %% Execution 返回
    EAS -->|session_id| DJ
    DJ -->|持久化| PG

    %% Shared Kernel 依赖
    Orchestration_Context -.->|使用| Shared_Kernel
    Execution_Context -.->|使用| Shared_Kernel

    %% Integration 可订阅
    Orchestration_Context -.->|事件发布| Integration_Context

    %% 样式定义
    style Orchestration_Context fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style Execution_Context fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Shared_Kernel fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style TaskGraph_External fill:#eceff1,stroke:#263238,stroke-width:1px,stroke-dasharray: 5 5
    style Integration_Context fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Infrastructure fill:#eceff1,stroke:#263238,stroke-width:1px,stroke-dasharray: 5 5
```

## 4. 战略设计决策记录

### 4.1 事件驱动 vs 轮询

**决策**：优先采用 PostgreSQL NOTIFY 事件驱动，辅以轮询作为补充

- **理由**：
  - TaskGraph 通过 NOTIFY 发布状态变更，事件驱动是自然选择
  - `PgNotifyEventListener` 实现异步事件监听，避免频繁轮询
  - `RunEventLoopTick` 用例提供手动轮询能力，用于启动初始工作流

### 4.2 SOP 驱动执行

**决策**：根据任务的 PlanningLevel 动态加载对应 SOP

- **理由**：
  - 不同粒度的任务需要不同详细程度的指导
  - SOP 封装在本地文件系统，便于维护和版本控制
  - SOP 包含 system_prompt 和 model_tier，直接影响 Execution 执行

### 4.3 进程内调用 Execution

**决策**：通过 `InProcessExecutionTrigger` 在进程内直接调用 Execution 用例

- **理由**：
  - Orchestration 和 Execution 在同一进程内，同步调用开销低
  - 简化跨进程通信复杂度
  - 保持调试和追踪的简洁性

---

## 修改记录

| 日期 | 修改内容 | 作者 |
|------|----------|------|
| 2026-03-20 | 初始版本创建 | DDD Strategic Designer |
