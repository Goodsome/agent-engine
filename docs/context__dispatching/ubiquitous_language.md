## 1. 核心领域术语表 (Core Domain Terminology)

在 Dispatching 上下文中，严禁使用诸如 `Task`, `Project`, `ScopeLevel` 等属于 Orchestration 或上游图谱的词汇。这里的开发语言必须高度聚焦于“执行”本身。

| 中文术语 (Chinese) | 英文映射 (English/Code) | 严格定义 (Strict Definition) |
| :--- | :--- | :--- |
| **派发指令 / 执行契约** | `DispatchCommand` | Orchestration 下发的不可变入参。包含目标 `SessionID`、必要的 `SystemPrompt`（若需初始化）和本次的 `UserInstruction`（具体任务内容）。它是本上下文唯一的驱动源。 |
| **底层执行器** | `UnderlyingExecutor` | 对底层大模型或 CLI 工具（如 `claude-code`）的抽象防腐层封装。在领域模型眼中，它是一个可以“启动”、“中断”并“产出日志”的黑盒。 |
| **会话挂载点** | `SessionMountPoint` | 物理层面上分配给某个 `SessionID` 的本地工作空间（如某个特定的隔离目录），供底层执行器在此执行文件读写等副作用操作。 |
| **执行回执** | `ExecutionReceipt` | Dispatching 返回给 Orchestration 的统一结果载体。它是一个包含状态标识的单一实体（例如拥有一个 status: SUCCESS | FAULT 字段）。根据状态的不同，它会选择性地携带有效产出 (Artifacts) 或故障详情 (ExecutionFault)。 |
| **产出物** | `Artifacts` | 包含在 `ExecutionReceipt` 中的数据，指代 Agent 本次执行取得的有效成果（例如：修改的文件路径列表、生成的摘要文本）。 |
| **执行故障** | `ExecutionFault` | 包含在 `ExecutionReceipt` 中的数据。系统将底层千奇百怪的错误（如 Token 超限、子进程 OOM、网络超时）统一翻译为枚举化的内部故障码，供上游做决策。 |

---

## 2. 领域不变量 (Domain Invariants)

这些是 Dispatching 在任何代码实现中都必须死守的底线原则：

1. **绝对上下文无知原则 (Absolute Context Ignorance Invariant):**
   * **规则：** `DispatchCommand` 中严禁包含 `ProjectID` 或 `TaskID`。Dispatching 内部的任何逻辑判断，绝不能依赖除了“当前指令内容”和“运行时状态”之外的信息。
   * **工程约束：** 如果在 Dispatching 的聚合或用例代码中看到了导入图谱模型或业务模型的包，即视为严重的架构违规。
2. **唯一执行源原则 (Single Execution Source Invariant):**
   * **规则：** 一个特定的 `SessionID` 在同一时刻，在底层只能拥有**一个**活跃的 `UnderlyingExecutor` 进程。
   * **工程约束：** 如果收到针对同一 `SessionID` 的并发 `DispatchCommand`，Dispatching 必须直接拒绝后续请求，并返回“资源被占用”的 `ExecutionReceipt`，绝不能在同一个目录下并发拉起两个大模型进程。
3. **单次履约原则 (Single-Try Obligation Invariant):**
   * **规则：** Dispatching 只负责“尽力而为”地执行一次指令。它**没有权利也没有义务**在遇到大模型断网或报错时进行循环重试（底层极短的网络抖动重试除外）。
   * **工程约束：** 代码中不允许存在对整个 Agent 运行流程的 `while(retry)` 逻辑。失败了就立刻组装 `ExecutionReceipt` 上报，由 Orchestration 的大脑来决定是否重发指令。
4. **彻底清理原则 (Thorough Cleanup Invariant):**
   * **规则：** 无论执行是自然结束、发生异常崩溃、还是被超时强制抹杀，分配给该次执行的系统资源（进程、线程、临时句柄）必须被彻底释放。

---

## 3. 核心行为规约 (Behavioral Specifications - BDD Style)

### 场景一：标准的代理执行闭环
> **说明：** Orchestration 下发指令，底层 Agent 顺利执行完毕。

* **Given (假设):** 系统接收到一个格式正确的 `DispatchCommand` (SessionID: 999)，且该 Session 当前处于空闲状态。
* **When (当):** 开始执行派发流。
* **Then (那么):** 系统必须：
  1. 为该 Session 分配/定位 `SessionMountPoint` (工作目录)。
  2. 实例化并启动 `UnderlyingExecutor`。
  3. 挂起当前协程，静默等待底层进程自然退出 (Exit Code 0)。
  4. 收集工作目录中的变更或标准输出，组装 `Artifacts`。
  5. 返回一个包含 `Artifacts` 的 `ExecutionReceipt`。

### 场景二：执行超时强制熔断 (The Breakwater Scenario)
> **说明：** 底层大模型由于遇到复杂死循环或者 API 无响应，长时间挂起。

* **Given (假设):** `UnderlyingExecutor` 正在运行 SessionID 999，且已持续 45 分钟未返回任何状态。
* **When (当):** 触发了预设的硬超时阈值 (Timeout Check)。
* **Then (那么):** 系统必须：
  1. 向底层子进程发送强制终止信号 (SIGKILL)。
  2. 回收 `SessionMountPoint` 相关的句柄资源。
  3. 翻译错误原因，组装 `ExecutionFault` (原因：TIMEOUT_EXCEEDED)。
  4. 立即向 Orchestration 返回 `ExecutionReceipt`。

### 场景三：防范并发执行污染
> **说明：** 由于上游事件风暴或重试机制缺陷，短时间内对同一个 Session 下发了两次相同的执行指令。

* **Given (假设):** `UnderlyingExecutor` 当前**正在**执行 SessionID 999 的指令。
* **When (当):** Dispatching 再次接收到一个针对 SessionID 999 的新 `DispatchCommand`。
* **Then (那么):** 系统必须：
  1. 拦截该新请求，**绝不**启动第二个底层进程。
  2. 立即针对新请求返回 `ExecutionFault` (原因：SESSION_BUSY_CONCURRENCY_REJECTED)。
  3. 保证原有的执行进程不受任何干扰，继续运行。
