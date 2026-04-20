## 1. 宏观架构风格 (Macro Architecture Style)

本上下文在 MVP 阶段采用**务实的整洁架构 (Pragmatic Clean Architecture)**。我们不强求完美的三层或四层物理隔离，但在逻辑思路上必须恪守“依赖倒置”的核心精神：

* **核心领域绝对纯粹：** 描述 `WorkCoordinate` (工作坐标) 和 `AgentSession` (记忆流) 的核心模型中，绝对不能引入任何关于数据库连接、消息队列 SDK 或外部 API 调用的第三方库。它们只能包含纯粹的业务状态和校验逻辑（例如校验会话唯一性不变量）。
* **应用层作为编排者：** 应用层（Use Cases）是本上下文的心脏。它负责接收网关转换来的触发器，组装业务流。在 MVP 阶段，应用层**被允许**直接通过异步协程 (Async/Await) 调用兄弟上下文（Registry 和 Dispatching）暴露的应用层接口，以换取极高的开发效率。
* **异步优先 (Async-First)：** 考虑到后续与大模型交互的长时间阻塞特性，本上下文内的所有用例入口、外部调用以及持久化操作，都必须基于原生异步 I/O 构建，确保单一进程能以极低的资源占用支撑海量的并发任务路由。

## 2. 核心组件交互模式 (Core Component Interaction Patterns)

系统在处理一个完整任务的生命周期时，将遵循以下交互技术路线：

### 2.1 入口驱动机制 (Inbound Triggering)
* **技术基座：** 基于 `event-hub` SDK 的异步消费者。
* **隔离策略：** 当 CLI 命令 `agent-engine listen` 启动时，事件网关（Event Gateway）开始监听网络。一旦接收到 `TaskReadyEvent` 或 `TaskReviewEvent`，网关负责完成 JSON 的反序列化与基础格式校验，并将其转化为纯粹的数据传输对象（DTO，即 `TaskReadyTrigger`）。随后，网关通过在内存中直接调用 Orchestration 应用层的异步入口函数，将控制权移交。

### 2.2 出口调度机制 (Outbound Dispatching)
* **同步查询，异步执行：**
  * 在向 Registry 子域获取角色画像时，虽然是跨上下文，但由于是内存级别的高速查询，采用直接的函数调用（返回 DTO）即可。
  * 在向 Dispatching 子域下达实际的 `DispatchCommand` 时，由于底层可能涉及启动 `claude-code` 子进程，这是一个耗时极长的操作。Orchestration 的应用层将通过 `await` 挂起当前任务，释放事件循环 (Event Loop) 给其他并发事件，直到 Dispatching 返回最终执行结果（成功/失败/异常栈）。

## 3. 状态管理与持久化策略 (State & Persistence Strategy)

Orchestration 需要持久化 `AgentSession` 以保证认知连续性，这方面的技术方向如下：

* **聚合根持久化：** `AgentSession` 作为聚合根，其状态变更是原子的。在落盘时，无论是使用关系型数据库（如 PostgreSQL/SQLite）还是文档型数据库，都必须将 `WorkCoordinate` 的四个维度（项目、任务、层级、范围）作为复合唯一索引（Composite Unique Index）建立在数据库表上。
* **并发控制 (Concurrency Control)：** 由于分布式系统可能会对同一个图谱节点重复投递“就绪”事件，数据库的复合唯一索引将作为最后一道防线。当并发创建相同坐标的 Session 时，应用层必须优雅捕获“违反唯一约束”的数据库异常（或使用乐观锁/Upsert 语法），并将其转化为“复用已有 Session”的业务逻辑，坚决捍卫“多维会话绝对唯一性”这一不变量。
* **幂等性保障 (Idempotency)：** 除了依靠数据库唯一索引拦截重复创建，应用层的入口处应集成基础的幂等校验（例如通过缓存记录最近处理过的 `TaskReadyEvent` ID），避免对已经在执行中的任务重复下发调度指令。

## 4. 事务边界与容错控制 (Transaction & Fault Tolerance)

MVP 阶段不引入复杂的分布式事务中间件，转而采用**基于异常的本地补偿 (Exception-Driven Local Compensation)**：

* **无跨上下文事务：** Orchestration 绝不会与 Dispatching 共享同一个数据库事务。Orchestration 在发起 Dispatching 调用前，就已经通过本地事务将 Session 的状态落盘。
* **Saga 退化为 Try-Catch：** 如果 Dispatching 在调用 Claude SDK 时发生不可逆的崩溃或超时，该异常必须向上抛出到 Orchestration 的应用层。
* **异常补偿闭环：** Orchestration 外层的 `try...except` (或等效错误处理块) 捕获到底层执行失败后，不进行数据库层面的自动回滚（因为业务已经真实发生过尝试）。它的职责是：
  1. 更新本地 `AgentSession` 的状态（如记录一次失败尝试）。
  2. 调用 `event-hub` SDK（通过网关代理），向 `task-graph` 发送一条类似 `TaskFailedEvent` 的外部事件，报告任务流转受阻，由上游图谱决定是重新发起还是人工介入。
