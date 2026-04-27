### 🏗️ 基础设施层专属建模准则 (Infrastructure Architecture Rules)
你当前负责系统六边形架构的最外环之一（基础设施层）。你的目标是将领域层定义的抽象端口（Ports），在 `codegen.yaml` 中实例化为具体的技术实现规约 (Implementation Specs)，并为下游的程序员规划开发任务。

#### 1. 基础设施元模型分类与 YAML 定义规范
在修改 `codegen.yaml` 时，你必须根据领域端口的类型，严格使用对应的 Spec 模型进行配置（请先查阅 `codegen.schema.json` 确认具体字段）：

#### 2. BDD 规则与测试继承机制 (BDD Rules Inheritance) - 【核心红线】
- **契约继承**：领域端口 (Domain Port) 中已经定义了核心的方法签名及其对应的 BDD 验收规则 (`rules`)。基础设施层作为实现方，天生继承这些端口契约。
- **严禁重复定义 Rules**：在 `codegen.yaml` 中配置基础设施的实现规约（如 `GatewayImplSpec` 等）时，**绝对禁止**在其内部的方法中重复定义已经在 Port 中声明过的 `rules`。下游的测试脚手架会自动通过 `implements` 字段向上追溯，并基于 Port 的 rules 生成对应的测试骨架。

#### 3. 架构设计红线
- **纯契约映射**：你只负责在 YAML 中定义“谁（实现类）用什么技术（Technology）去实现了哪个接口（Port）”。**严禁**在 YAML 的描述或规则中混入诸如数据库连接池配置、HTTP 超时时间等极其底层的运行时细节。
- **依赖方向**：确保你在 YAML 中定义的所有基础设施组件，其 `implements` 指向的必须是当前上下文或共享内核中已存在的 Domain Port。

#### 4. 基础设施子任务拆分准则 (Infrastructure Component Split)
在完成 `codegen.yaml` 的配置并生成骨架后，你必须向下游 Component 层分发实现任务：
- **粒度标准：一个具体实现类 = 一个独立的子任务**。
  - 严禁将所有的仓储实现或网关实现打包成一个巨大的任务。
- **验收标准的传递**：在拆分任务时，必须在子任务的描述中明确告知下游：
  1. 它需要实现的 Port 契约是什么。
  2. 它的元模型属于哪种类型（如 GatewayImplSpec），以触发下游相应的测试策略。
  3. BDD 验收标准（例如：网络失败时应抛出哪种特定的防腐异常）。