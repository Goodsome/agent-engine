## 1. 宏观架构风格 (Macro Architecture Style)

如果说 Orchestration 是状态驱动的，那么 Dispatching 就是**纯粹的行为驱动与无状态的 (Stateless)**。

本上下文在技术架构上采取**防腐层优先 (Anti-Corruption Layer First)** 的设计哲学：
* **内部纯粹性：** 领域层只认识 `DispatchCommand` 和 `ExecutionReceipt`。
* **边界防御性：** 基础设施层（Infrastructure）包含了与操作系统、子进程、大模型 SDK 打交道的所有“脏代码”。这一层必须被极其严密地封装，确保任何诸如“管道破裂 (Broken Pipe)”、“子进程僵死”的系统级异常，绝不能泄漏到 Dispatching 的应用层，更不能抛给 Orchestration。
* **无状态运行：** Dispatching 不拥有自己的数据库。它的状态存在于内存中的协程和操作系统的进程表中。一旦回执生成并交付，它对该任务的所有记忆即刻销毁。

## 2. 核心组件交互模式 (Core Component Interaction Patterns)

在这个无状态的上下文中，数据的流转呈现单向的漏斗形：

### 2.1 接收与启动机制 (Inbound Dispatch)
* **同步校验，异步执行：** Orchestration 通过应用层的直接调用传入 `DispatchCommand`。Dispatching 首先进行轻量级的同步校验（例如检查指令的完整性、本地工作目录是否可写）。一旦校验通过，立即进入 `await` 异步等待状态，将繁重的物理执行推入后台。

### 2.2 底层执行与适配机制 (Underlying Execution Adapter)
* **子进程沙盒化封装：** 针对 `claude-agent-sdk`（底层拉起 CLI），必须在 Dispatching 的基础设施层实现一个专门的执行器适配器 (Executor Adapter)。

## 3. 并发与资源隔离策略 (Concurrency & Resource Isolation)

由于 Dispatching 是直接操作操作系统资源（进程、文件系统）的网关，必须在此确立严格的物理隔离策略：

* **文件系统隔离 (FS Isolation)：** 每个 `SessionID` 在执行时，必须被分配一个独立的、带有写权限隔离的本地工作目录（即 `SessionMountPoint`）。执行器启动时，必须将其工作路径 (`cwd`) 严格限制在该目录下，防止不同 Agent 并发执行时互相覆盖文件或产生幻觉。
* **内存级别的防并发锁：** 尽管 Orchestration 在上层有并发控制，Dispatching 内部仍需设立最后一道防线。可以使用基于内存的异步锁（如 `asyncio.Lock` 字典，以 `SessionID` 为键），确保针对同一个会话标识，物理层面上绝对不可能有两个并发的子进程被拉起。

## 4. 容错、熔断与清理契约 (Fault Tolerance & Cleanup Contract)

这是 Dispatching 作为“防波堤”最重要的技术规约，必须通过强制的代码范式（如 `try...finally` 块或上下文管理器）来保证：

* **硬超时熔断 (Hard Timeout Circuit Breaker)：**
  所有的异步底层调用必须包裹在超时控制中（例如 `asyncio.wait_for`）。一旦触发超时，Dispatching 必须放弃等待。
* **进程安全抹杀 (Safe Process Termination)：**
  当发生超时、被上游主动取消、或者捕获到致命异常时，Dispatching 必须执行优雅降级销毁：首先尝试发送 `SIGTERM` 请求 CLI 自行退出；若在极短时间内未退出，必须果断发送 `SIGKILL` 强制终止，绝不允许产生孤儿进程 (Orphan Process)。
* **兜底状态翻译 (Fallback Translation)：**
  在 `catch/except` 的最外层，必须有一个“兜底翻译器”。无论是 `TimeoutError`、`OSError` 还是其他未预料的底层崩溃，翻译器负责将异常的堆栈信息截断，提取核心原因，将其赋值给 `ExecutionReceipt` 的 `fault` 字段，并将主状态标记为 `FAULT`，最终安全地将其返回给 Orchestration。
* **物理痕迹清理 (Artifacts Cleanup)：**
  在 `finally` 块中，无论执行成功与否，必须释放掉对标准输入/输出流的文件句柄占用，确保系统句柄不被泄露。
