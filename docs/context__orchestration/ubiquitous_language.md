## 1. 核心领域术语表 (Core Domain Terminology)

在这个限界上下文中，团队的所有成员（包括研发、测试、甚至是未来的产品经理）在讨论系统行为时，**必须且只能**使用以下术语及其严格定义：

| 中文术语 (Chinese) | 英文映射 (English/Code) | 严格定义 (Strict Definition) |
| :--- | :--- | :--- |
| **工作坐标** | `WorkCoordinate` | 唯一锁定一个工作上下文的复合值对象。由四个维度构成：`ProjectID` (项目标识) + `TaskID` (根任务标识) + `ScopeLevel` (层级，如 atomic) + `ScopeDetails` (层级具体细节，如 context_name 或 domain_name)。 |
| **记忆流 / 会话** | `AgentSession` | Agent 在特定“工作坐标”下的连贯历史上下文。它是与大模型持续交互的载体，包含系统设定（System Prompt）和所有历史对话（History）。 |
| **层级角色** | `ScopeRole` | 与 `ScopeLevel` 绑定的 AI 身份画像（如：架构师、基础编码员），由注册中心提供，决定了 Agent 的具体行为准则。 |
| **执行契约 / 派发指令**| `DispatchCommand` | Orchestration 构建的不可变对象，是下发给底层派发引擎的最终命令。包含：`SessionID` + `SystemPrompt` (如果新建) + `UserInstruction` (本次任务内容)。 |
| **就绪触发器** | `TaskReadyTrigger` | 由外部事件网关转化而来的内部指令，表示某个图谱节点的前置依赖已满足，请求 Orchestration 拉起执行流。 |
| **审查触发器** | `TaskReviewTrigger` | 由外部事件网关转化而来的内部指令，明确携带了“审查目标”以及“审查者工作坐标”，请求拉起审查流。 |

---

## 2. 领域不变量 (Domain Invariants)

不变量（Invariants）是系统在任何时刻都**绝对不能被打破**的业务规则。它们通常需要在聚合根（Aggregate Root）内部或用例的入口处进行强校验。

1. **会话多维唯一性原则 (Session Singularity Invariant):**
   * **规则：** 对于任意一个给定的 `WorkCoordinate`（ProjectID + TaskID + ScopeLevel + ScopeDetails），在系统中**最多只能存在一个**存活的 `AgentSession`。
   * **工程约束：** 试图为已存在的 `WorkCoordinate` 创建新 `AgentSession` 的操作必须被拒绝，并强制复用已有 Session ID。
2. **审查者身份不可篡改原则 (Reviewer Identity Immutable Invariant):**
   * **规则：** Orchestration 严禁内部推断审查者。`TaskReviewTrigger` 中必须显式包含审查者的 `WorkCoordinate` 和被审查的产出物引用。
   * **工程约束：** 如果审查触发器中缺失 `reviewer_work_coordinate`，该事件必须直接被抛弃或标记为“无效请求 (Dead Letter)”，禁止系统采用“默认上一级”的 fallback 逻辑。
3. **职责单向隔离原则 (One-way Responsibility Invariant):**
   * **规则：** Orchestration 不持有任务状态机（如 Pending -> InProgress -> Done）。它只负责发送 `DispatchCommand` 并将底层返回的最终结果通过网关通知给 `Task Graph`。
   * **工程约束：** Orchestration 的数据库表（如果存在）中，不能有“任务完成度”或“图谱依赖结构”的字段。

---

## 3. 核心行为规约 (Behavioral Specifications - BDD Style)

为了让未来的测试用例（TDD/BDD）有据可依，我们将核心编排流转化为明确的 `Given / When / Then` 业务行为规约。

### 场景一：首次分配特定坐标的开发任务
> **说明：** 外部抛出任务，Orchestration 发现该工作坐标下尚无历史会话。

* **Given (假设):** 系统存在一个有效的外部能力注册中心，且本地数据库中**不存在**匹配当前 `WorkCoordinate` 的 `AgentSession`。
* **When (当):** Orchestration 接收到一个 `TaskReadyTrigger` (任务就绪触发器)。
* **Then (那么):** 系统必须：
  1. 向注册中心请求该层级对应的 `ScopeRole` (含 System Prompt)。
  2. 生成并持久化一个新的 `AgentSession`，将其与该 `WorkCoordinate` 绑定。
  3. 组装一个携带全新 `SessionID` 和 `SystemPrompt` 的 `DispatchExecutionCommand`。
  4. 将指令投递给底层派发上下文。

### 场景二：同一工作坐标下的连续任务接力
> **说明：** 同一个任务下的同一个层级，又有了新的小任务（例如 atomic 层写完了 service，现在轮到写 repository）。

* **Given (假设):** 本地数据库中**已经存在**匹配当前 `WorkCoordinate` 的活跃 `AgentSession` (SessionID: 12345)。
* **When (当):** Orchestration 接收到一个新的 `TaskReadyTrigger`。
* **Then (那么):** 系统必须：
  1. 不向注册中心重新拉取 System Prompt（因为角色已固定）。
  2. 提取已存在的 `SessionID` (12345)。
  3. 组装一个不带初始化设定的、仅追加本次内容的 `DispatchExecutionCommand`。
  4. 确保底层派发器将在历史上下文的基础之上继续对话。

### 场景三：接收跨层级审查任务
> **说明：** 底层代码写完，图谱引擎抛出事件，指明由上下文层的架构师进行 Review。

* **Given (假设):** Orchestration 接收到一个 `TaskReviewTrigger`，且该触发器中明确指定了 Reviewer 的 `WorkCoordinate` (例如：ScopeLevel = context)。
* **When (当):** 开始执行审查编排流。
* **Then (那么):** 系统必须：
  1. 严格使用触发器中指定的 Reviewer `WorkCoordinate` 去检索对应的 `AgentSession`。
  2. （由于是从上向下拆解的，该父层级 Session 必然存在）提取该 Reviewer 的 `SessionID`。
  3. 将“被审查的产出物信息”和“审查指南”打包。
  4. 下发 `DispatchReviewCommand`，确保大模型是以最初做设计的“架构师”记忆来审视这份代码。
