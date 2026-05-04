## 1. 业务愿景 (Business Vision)

`Agent Registry` 是整个 `agent-engine` 的**知识库与身份管理中心**。

在复杂的软件工程自动化流转中，不同的阶段（从宏观架构到微服务定义，再到具体的代码实现）对 AI 的认知要求截然不同。`Agent Registry` 的愿景是充当一个高可靠的“黄页”，它确立了系统中各种 Agent 角色的准入标准，并作为标准作业程序 (SOP) 的唯一真相源。它屏蔽了提示词编写的琐碎细节，让系统能够通过简单的“层级标签”找到最专业的“数字专家”。

## 2. 核心职责边界 (Core Responsibilities & Boundaries)

* **职责所在 (In-Scope):**
    * **角色定义与映射：** 维护任务层级（Scope Level）与 Agent 角色画像（Role Profile）之间的静态映射关系。
    * **SOP 提示词管理：** 存储并供应不同层级任务所需的系统提示词（System Prompts）。这些提示词包含了该层级 Agent 的思考模型、遵循的架构原则（如 DDD/Clean Architecture）以及输出规范。
    * **技能描述：** 定义不同角色所具备的能力边界（如：架构师负责定义领域模型，而编码员负责具体语法实现）。
* **坚决隔离 (Out-of-Scope):**
    * **动态会话维护：** 坚决不记录任何关于 `SessionID` 或历史对话的信息（这是 Orchestration 和 Dispatching 的职责）。
    * **任务状态感知：** 它不知道任务是否已经完成，只负责在被询问时提供“该怎么做”的指导方案。
    * **模型调用：** 坚决不参与任何与大模型 API 的直接交互。

## 3. 核心业务流程 (Core Workflows / User Stories)

本上下文目前聚焦于最核心的“策略供应”流程：

### 3.1 身份与策略检索 (Identity & Strategy Retrieval)
当 Orchestration 接收到一个新坐标的任务，需要确定“谁来做”时：
1.  **接收层级请求：** Registry 接收到一个包含 `ScopeLevel`（如 `architecture`）的查询请求。
2.  **定位 SOP 模板：** 内部查询逻辑命中预设的“架构设计层级”规则。
3.  **提取角色规格：** 检索该层级对应的 Agent 画像（例如：“DDD 架构专家”）。
4.  **下发执行蓝图：** 返回包含角色名称、完整的系统提示词（System Prompt）以及建议的工具集。此时，Orchestration 获得了一份完整的“执行锦囊”。

## 4. 任务层级与 SOP 规约 (Scope Levels & SOP Specifications)

在 MVP 阶段，本上下文通过四种核心层级来覆盖软件开发的生命周期。你可以通过下方的交互演示来探索不同层级在 Registry 中的定义差异：

## 5. 关键业务约束 (Business Constraints)

1.  **单向解析约束：** 解析方向必须是 `ScopeLevel -> Role/SOP`。Registry 严禁根据任务的具体内容（如具体的代码逻辑）动态生成提示词，它只提供标准的、基于层级的模板。
2.  **版本稳定性原则：** SOP 提示词一旦被 Orchestration 用于初始化一个 `AgentSession`，在该 Session 的生命周期内，Registry 对该层级提示词的修改不应影响已存在的会话，以保证认知的连贯性。
3.  **解耦独立性：** Registry 的实现不应依赖任何特定的 LLM 特性。它输出的是通用的自然语言指令，确保系统未来可以平滑切换底层模型。
