## 1. 全局上下文概览 (Context Overview)

在当前的研发自动化生态中，涉及以下主要限界上下文（Bounded Contexts）：

* **Task Graph Context (外部上游):** 负责任务拆解、AND/OR 依赖图谱管理以及任务状态的流转。
* **Event Hub Context (全局基础设施):** 统一定义全局领域事件的 Schema 与版本（发布语言）。
* **Agent Engine - Orchestration Context (内部核心):** 引擎大脑，包含入站事件的防腐解析、工作流编排、SOP 解析与派发决策。
* **Agent Engine - Agent Registry Context (内部支撑):** 维护 Agent 角色、能力、提示词与任务元数据的静态配置映射。
* **Agent Engine - Dispatching Context (内部核心):** 负责纳管具体的 Agent 会话，处理与底层大模型 CLI 的交互闭环。

---

## 2. 上下文映射与协作关系 (Context Mapping & Integration)

### 2.1 Task Graph [U] ➔ [D] Orchestration (含防腐接入层)
* **协作模式：发布语言 (Published Language, PL) + 遵奉者 (Conformist, CF)**
* **业务关系描述：**
    `Task Graph` 是任务事件的唯一真相源。双方通过 `event-hub` SDK 定义的标准事件模型作为沟通的**发布语言 (PL)**。`Orchestration` 上下文的外部接口层（原事件网关职责）完全信任并**遵奉 (CF)** 这个模型，直接消费任务元数据，过滤后将其转换为内部的 `TaskReadyTrigger` 等指令，直接驱动编排流。

### 2.2 Orchestration [D] ➔ [U] Agent Registry
* **协作模式：客户/供应商 (Customer/Supplier, C/S)**
* **业务关系描述：**
    编排上下文 (Orchestration) 收到触发器后，作为客户向 Agent 注册中心 (Registry) 发起业务查询：“请提供 `context` 层级的角色画像与蓝图”。Registry 返回匹配的实体与模板，实现了业务流转逻辑与 AI 角色提示词的物理分离。

### 2.3 Orchestration [U] ➔ [D] Dispatching
* **协作模式：隔离通道 (Separate Ways) / 客户供应商 (C/S)**
* **业务关系描述：**
    编排组装完毕后，作为上游将包含 `SessionID` 和 `SystemPrompt` 的不可变 `DispatchCommand` 下发给 Dispatching。派发上下文负责拉起子进程、监控超时、隔离错误，最终通过单向的 `ExecutionReceipt` 返回成功产物或故障快照。

---

## 3. 上下文映射图解 (Logical Map)

*注：箭头指向表示数据/控制流的下游依赖方向。*

[Task Graph] (任务建模)
      │
      │ PL (通过 event-hub 定义的标准事件) / CF (遵奉消费)
      ▼
[Orchestration] (编排核心，自带入站适配器)
      │           │
      │ C/S       │ C/S (下发具体会话指令)
      ▼           ▼
[Agent Registry] [Dispatching]
(能力注册黄页)    (派发与防波堤)