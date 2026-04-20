## 1. 宏观架构风格与演进策略 (Architecture Style & Evolution)

**当前阶段 (MVP): 实用型模块化单体 (Pragmatic Modular Monolith)**
在 MVP 阶段，`agent-engine` 作为单一进程运行，并采用务实的上下文集成策略。为了兼顾开发效率与领域边界，内部跨上下文交互**允许在应用层（Application Layer / Use Cases）进行直接的异步引用与调用**。

**未来演进路径 (Future Roadmap):**
1. **防腐与倒置:** 随着业务复杂度上升，逐步引入接口隔离原则 (ISP)，将直接的用例引用重构为依赖注入 (DI) 的接口调用。
2. **事件总线统一:** 内部状态变更通知将从“直接调用”重构为“领域事件发布”，并复用 `event-hub-sdk` 提供进程内（或跨进程）的 Pub/Sub 能力，实现上下文的彻底物理与逻辑解耦。

---

## 2. 外部集成契约 (External Integrations)

定义系统与外部世界（业务上游与底层执行引擎）的通信契约。

### 2.1 任务事件接入 (Task Graph ➔ Agent Engine)
* **通信模式:** 异步发布/订阅 (Pub/Sub)
* **技术底座:** `event-hub` SDK
* **集成契约:**
    * 网关层 (Event Gateway) 监听 `event-hub` 分发的外部事件。
    * 接收到事件后，不再做复杂的内部总线路由，而是**直接异步调用** Orchestration 暴露的入口用例（Use Case）来启动业务流。

### 2.2 Agent 执行引擎交互 (Dispatching ➔ Claude Agent SDK)
* **通信模式:** 异步 SDK 调用 (Async SDK Invocation)
* **技术底座:** `claude-agent-sdk` (作为基础设施层适配器)
* **集成契约:**
    * **能力封装 (Encapsulation):** Dispatching 上下文严格屏蔽底层执行引擎的实现细节。无论 SDK 底层如何运作，Dispatching 统一通过 `claude-agent-sdk` 提供的标准异步接口进行 Agent 会话的拉起、指令下发与结果获取。
    * **边界防御 (Boundary Defense):** 鉴于 Agent 执行过程的不可控性，Dispatching 必须在 SDK 调用层做好异常捕获与超时控制，确保底层执行库的任何崩溃或挂起，都不会导致主引擎进程的阻塞或雪崩。
    * **状态映射 (State Mapping):** Dispatching 的核心职责是将 SDK 返回的底层执行状态，转化为 `agent-engine` 内部可理解的领域状态（如：`DispatchingFailed`, `AgentSessionCompleted`）。

---

## 3. 内部跨上下文通信契约 (Internal Cross-Context Communication)

系统内部在 MVP 阶段采用最高效的直接调用模式，但依托于异步协程保证高并发吞吐。

### 3.1 跨上下文业务编排 (Orchestration ➔ Registry & Dispatching)
* **通信模式:** 异步用例直接调用 (Async Use Case Invocation)
* **技术底座:** 语言原生的异步协程 (Async/Await)
* **集成契约:**
    * **单向依赖:** Orchestration 作为协调者，允许直接导入（Import）并实例化 Registry 和 Dispatching 上下文中的 Application 层用例。
    * **异步非阻塞:** 所有的跨上下文调用必须是异步函数（`async def`）。例如，Orchestration 等待 Dispatching 完成 SDK 的调用时，当前协程挂起，让出 CPU 给其他任务图谱事件。
    * **DTO 传递:** 尽管是直接调用，但参数传递**严禁直接传递领域实体 (Entity)**。必须通过简单的数据传输对象 (DTO) 或基本数据结构（如字典、数据类）进行通信，防止领域逻辑跨界污染。

---

## 4. 状态与事务一致性 (State & Transactional Consistency)

由于采用了纯异步的用例调用模式，事务的控制依赖于代码的执行顺序和异常捕获策略。

* **本地防断点 (Local State Persistence):**
    鉴于 Agent 任务的执行可能耗时较长，Orchestration 在发起对 Dispatching 的异步调用前，应将当前核心业务流程的状态落盘（更新本地 DB），防止引擎重启导致任务丢失。
* **基于异常的 Saga 补偿 (Exception-Driven Saga):**
    在没有事件总线的 MVP 阶段，长事务的最终一致性由 `try...catch...finally` 块保障。
    如果 Dispatching 抛出 SDK 执行异常，Orchestration 的外层 `await` 捕获该异常后，负责执行本地状态的更新（如标记为失败），并通过事件网关向上游系统（Task Graph）发送任务异常报告。
