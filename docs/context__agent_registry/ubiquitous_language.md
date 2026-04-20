### `docs/contexts__agent_registry/ubiquitous_language.md`

## 1. 核心领域术语表 (Core Domain Terminology)

在 `Agent Registry` 上下文中，所有词汇都必须围绕“静态配置”与“能力模板”展开，严禁混入任何与“运行时 (Runtime)”或“任务状态”相关的动态词汇。

| 中文术语 (Chinese) | 英文映射 (English/Code) | 严格定义 (Strict Definition) |
| :--- | :--- | :--- |
| **任务层级** | `ScopeLevel` | 标识软件开发维度的枚举值或值对象。当前标准包含：`project` (战略), `context` (上下文), `architectural` (架构), `atomic` (原子)。这是本上下文的核心查询主键。 |
| **角色画像** | `RoleProfile` | 描述 Agent “是谁”的实体数据。包含角色的显示名称（如“领域建模师”）、核心职责简述以及能力边界。 |
| **系统提示词 / SOP 模板** | `SystemPromptTemplate` | 赋予 Agent “如何思考与行动”的硬编码指令集。它是一段大段的文本模板，内含基于特定 `ScopeLevel` 的标准作业程序 (SOP)、输出格式要求及防幻觉约束。 |
| **工具/能力集** | `CapabilitySet` | 描述该角色被允许调用的外部工具列表。例如：原子层可能拥有 `WriteFile` 和 `RunLinter` 能力，而战略层可能只拥有 `ReadMarkdown` 能力。 |
| **执行蓝图** | `ExecutionBlueprint` | 注册中心组装后返回给 Orchestration 的完整结果载体 (DTO)。它是一个值对象，内部完整打包了命中查询的 `RoleProfile`, `SystemPromptTemplate` 和 `CapabilitySet`。 |
| **蓝图查询指令** | `BlueprintQuery` | Orchestration 发起的请求对象。通常仅需包含目标的 `ScopeLevel`。 |

---

## 2. 领域不变量 (Domain Invariants)

这些不变量确保了 Registry 作为一个“只读型知识库”的纯粹性与稳定性：

1. **绝对无状态原则 (Absolute Stateless Invariant):**
   * **规则：** Registry 坚决不维护或记录任何关于 `TaskID`, `ProjectID` 或 `SessionID` 的信息。
   * **工程约束：** 它的对外查询接口 (`get_blueprint`) 的入参中，绝不允许出现具体业务的 ID。对它而言，一千个不同的项目请求 `atomic` 层级的蓝图，它都视为同一种请求。
2. **幂等与确定性映射原则 (Deterministic Mapping Invariant):**
   * **规则：** 在系统配置未发生版本更新的前提下，给定一个合法的 `ScopeLevel`，Registry 必须永远返回内容完全一致的 `ExecutionBlueprint`。
   * **工程约束：** 不允许在返回的 System Prompt 中动态植入诸如“当前时间”、“随机数”等非确定性变量。所有的动态上下文植入都应交由 Orchestration 去完成。
3. **封闭枚举拦截原则 (Closed Enumeration Interception):**
   * **规则：** Registry 只对已注册的、合法的 `ScopeLevel` 提供服务。
   * **工程约束：** 若上游传入了一个未知的层级标识（如拼写错误的 `atmoic` 或尚未支持的 `deployment` 层），Registry 必须立即抛出明确的领域异常（如 `UnsupportedScopeLevelException`），**绝不允许**静默降级或返回一个“通用/默认”的 Agent 蓝图。

---

## 3. 核心行为规约 (Behavioral Specifications - BDD Style)

### 场景一：标准的层级蓝图检索
> **说明：** Orchestration 准备分配一个编写代码的任务，向 Registry 索要原子层级的 Agent 设定。

* **Given (假设):** 系统已从本地项目目录加载了 **Markdown 配置文件 (如 `atomic.md`)**，且其 Frontmatter 中正确定义了映射关系。
* **When (当):** Orchestration 发起一个 `BlueprintQuery(scope_level="atomic")`。
* **Then (那么):** 系统必须：
  1. 检索内存中的 Markdown 索引，命中 `atomic` 层级。
  2. 提取 Frontmatter 中的角色名称（如 "Software Developer"）。
  3. 提取 Markdown 正文作为 `SystemPromptTemplate`。
  4. 将这些信息组装为不可变的 `ExecutionBlueprint` 值对象。
  5. 成功返回该蓝图。

### 场景二：未知层级的防御性拦截
> **说明：** 外部事件可能由于 Bug 传递了一个错误的或暂不支持的任务层级。

* **Given (假设):** 系统的配置目录中**仅存在** `project.md`, `context.md`, `architectural.md`, `atomic.md` 四个配置文件。
* **When (当):** Orchestration 发起一个 `BlueprintQuery(scope_level="infrastructure")`。
* **Then (那么):** 系统必须：
  1. 在配置库检索时发生未命中 (Miss)。
  2. 拒绝继续处理。
  3. 立即抛出 `UnsupportedScopeLevelException`，通知调用方该层级的 Markdown 配置不存在。

### 场景三：配置更新时的读隔离 (热载入特性)
> **说明：** 开发者修改了 Markdown 配置文件，优化了架构师的提示词。

* **Given (假设):** 系统支持配置的基于文件系统的热重载 (Hot-Reloading)。
* **When (当):** `architectural.md` 文件在磁盘上被修改并保存。
* **Then (那么):** 系统必须：
  1. 重新解析该 Markdown 的 Frontmatter 和正文，并验证格式。
  2. 将内存中该 `ScopeLevel` 对应的 `ExecutionBlueprint` 原子化替换。
  3. **绝对隔离：** 这种修改只会命中下一次全新的 `BlueprintQuery`，严禁通过任何手段去干涉或刷新那些在 Dispatching 中基于老版本 Prompt 运行的存量 `AgentSession`。