## 1. 宏观架构风格 (Macro Architecture Style)

本上下文采取**数据驱动的插件化架构 (Data-Driven Plugin Architecture)**。

* **配置即代码 (Config-as-Code)**：所有的 Agent 身份设定与 SOP 提示词不硬编码在程序逻辑中，也不存储在远程数据库，而是作为项目资源文件（Markdown）存在于代码仓库中。
* **只读性与确定性**：Registry 在运行时被视为一个只读的“知识索引”。它不负责修改提示词，仅负责解析、缓存并高效供应。
* **领域模型与基础设施分离**：领域层定义 `ExecutionBlueprint`（执行蓝图）的结构，而基础设施层负责从文件系统中检索并解析这些 Markdown 文件。

## 2. 核心组件交互模式 (Core Component Interaction Patterns)

### 2.1 蓝图解析流 (Blueprint Parsing Flow)
* **Markdown 标准协议**：采用“Frontmatter + Content”的标准格式。Markdown 顶部的 YAML 区块（Frontmatter）存储角色元数据（如角色名、权限集），正文部分（Content）存储完整的 System Prompt。
* **动态加载机制**：当 `agent-engine` 启动或接收到首次查询请求时，Registry 的加载器扫描指定资源目录，将所有 Markdown 文件转化为内存中的蓝图对象映射表。

### 2.2 跨上下文交互 (Cross-Context Interaction)
* **内存级同步响应**：由于蓝图已预加载至内存，Orchestration 对 Registry 的调用应被视为**极低延迟的同步操作**。即使在异步框架下，该操作也应通过非阻塞的内存查询立即返回 DTO。

## 3. 存储与加载策略 (Storage & Loading Strategy)

### 3.1 提示词持久化策略
* **文件格式规约**：使用 Markdown (`.md`) 作为唯一持久化格式。Markdown 的易读性使得非开发人员（如提示词工程师、产品经理）也能直接通过文本编辑器维护 Agent 的“灵魂”。
* **索引键设计**：文件名或 Frontmatter 中的 `scope` 字段将作为逻辑索引。例如，加载器会将 `atomic.md` 自动映射为 `ScopeLevel.ATOMIC` 的蓝图源。

### 3.2 加载与缓存机制
* **热载入支持 (Hot-Reloading)**：在开发环境下，Registry 应支持监视文件系统变更。一旦 Markdown 文件被保存，内存中的蓝图映射应自动更新，实现“保存即生效”的调试体验。
* **生产环境预加载**：在生产环境下，为了保证性能与确定性，系统在初始化阶段完成一次性解析，后续查询全部命中内存缓存。

## 4. 扩展性与演进策略 (Evolutionary Strategy)

### 4.1 提示词版本管理
* **Git 驱动的版本控制**：利用 Git 的 Tag 和 Commit 记录来追踪 SOP 的演进。如果某个版本的提示词导致 Agent 表现不佳，可以利用 Git 回滚迅速恢复认知。
* **多模型适配 (Future)**：未来可以在 Markdown 的 Frontmatter 中增加模型参数限制（如 `temperature`, `max_tokens`），甚至针对不同厂商的模型提供不同的 `.md` 变体（如 `atomic.claude.md` 和 `atomic.gpt4.md`）。

### 4.2 角色权限集管理
* **能力描述符 (Capability Descriptors)**：在 Markdown 配置中预留工具集标识。Registry 负责解析这些标识，并将其转化为 Dispatching 能够理解的权限开关，从而限制不同层级 Agent 的操作范围（例如：`atomic` 层可以写文件，而 `project` 层只能读文件）。
