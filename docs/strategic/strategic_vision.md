## 1. 业务愿景与北极星目标 (Vision & North Star)

**业务愿景 (Vision):**
`agent-engine` 旨在成为纯粹、高效的 Coding Agent 调度与路由网关。作为下游系统，它通过 `event-hub` 统一监听并接管来自 `task-graph` 的核心领域事件（如基于图逻辑的任务创建与状态流转）。引擎基于事件上下文与标准作业程序 (SOP)，智能匹配并下发任务至合适的 Agent 会话中，彻底解耦“任务依赖管理”与“AI 代理执行”，实现研发工作流的自动化闭环。

**北极星目标 (North Star Metric):**
* **端到端派发成功率 (End-to-End Dispatch Success Rate):** 从接收 `task-graph` 事件到成功拉起 Agent 会话并回传有效结果的闭环成功比例。
* **路由匹配准确度 (Routing Accuracy):** 任务元数据（如项目级、上下文级、原子级）与所派发 Agent 能力模型的一致性，确保零越权、零错位执行。

---

## 2. 领域划分 (Domain Categorization)

基于“高内聚、低耦合”的原则，我们将 `agent-engine` 的业务空间划分为以下子域，明确剥离任务建模逻辑，聚焦调度与派发。

### 2.1 核心域 (Core Domain)
*系统的绝对核心壁垒。负责理解业务流程并协调底层的 AI 资源。*

* **编排子域 (Orchestration):**
    系统的“大脑”与入海口。**它包含底层的事件防腐层（原事件网关）**，负责专门对接 `event-hub` SDK，将外部事件转换为内部的触发器指令。在核心领域层，它结合预设的标准作业程序 (SOP) 决定下一步动作。它不关心具体的执行细节，只负责宏观的流程把控与会话上下文组装。
* **派发子域 (Dispatching):**
    系统的“手脚”。负责接收编排子域下达的指令，管理具体的 Agent Session 生命周期，处理 LLM（如 `claude-code` CLI）交互的重试、限流与子进程控制，并将执行结果格式化后反馈给上游。

### 2.2 支撑域 (Supporting Domain)
*支撑核心业务运转，提供必要的数据转化与元数据管理能力。*

* **Agent 能力注册子域 (Agent Registry & Capability):**
    解决系统耦合的关键。作为 Agent 技能和角色的“黄页”。它维护任务层级（project/context/architecture/component）与具体 Agent 角色、系统提示词 (System Prompt)、可用工具 (Tools) 之间的映射关系。确保上游系统只需发出客观事件，而由本子域动态决定“谁来做”以及“怎么做”。

### 2.3 通用域 (Generic Domain)
*采用成熟标准或基础设施，MVP 阶段可仅做接口预留，不投入自研精力。*

* **可观测性与审计子域 (Observability & Audit) `[MVP后演进]`:** 记录 Agent 执行的完整轨迹（Prompt/Response 日志归档）、Session 链路追踪。
* **通知告警子域 (Notification) `[MVP后演进]`:** 当派发失败、Agent 持续报错或触发人工审核卡点时，通过企业通讯工具进行告警触达。

---

## 3. 核心域价值评估准则 (Value Assessment Criteria)

在后续的迭代中，任何新需求进入 Backlog 时，首要任务是评估其对“核心域（编排与派发）”的价值。评估准则如下：

1.  **职责纯粹性：** 该需求是否试图将“任务图谱的依赖逻辑”引入本系统？如果是，坚决驳回，将其推回给 `task-graph`。
2.  **派发健壮性：** 该需求是否能增强 Dispatching 上下文处理大模型不稳定性的能力？（例如：增加针对特定错误码的自动 Fallback 机制）。
3.  **配置隔离性：** 新增的 Prompt 模板或模型参数是否收敛在了 Agent Registry 中，而没有硬编码在 Orchestration 的业务流中？