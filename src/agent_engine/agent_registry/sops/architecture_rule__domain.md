### 🧱 领域层专属建模准则 (Domain Architecture Rules)
你当前处于六边形架构的最内环（核心域）。你的世界里只有面向对象原则、领域事件与业务不变量。**严禁**在模型中引入任何与数据库 (ORM)、网络协议 (HTTP)、Web 框架或文件 I/O 相关的技术细节。

#### 1. DDD 战术构建块规范
在修改 `codegen.yaml` 的 `domain` 节点时，必须严格遵循以下组件的职责约束：
- **Aggregate (聚合根)**：封装强一致性的业务实体与值对象，作为数据访问与修改的唯一入口。负责维护业务不变量。
- **Entity (实体)**：具唯一标识且生命周期内状态可变，包含核心业务状态与行为。
- **Value Object (值对象)**：无唯一标识，通过属性组合比较相等性。必须是不可变对象，用于封装内聚的属性或简单计算。
- **Enum (枚举)**：固定的业务状态常量集合。
- **Domain Event (领域事件)**：描述领域内已发生且对业务有影响的事实。
- **Domain Exception (领域异常)**：违反领域规则时抛出的业务级异常。
- **Domain Port (领域端口)**：领域层依赖的外部能力契约（Interface），如调用外部服务。**严禁包含实现细节**。
- **Domain Service (领域服务)**：编排跨越多个聚合的无状态领域逻辑。
- **Repository (仓储接口)**：管理聚合根生命周期的持久化契约接口，绝对不包含数据库层面的实现。

#### 2. 领域层子任务拆分例外原则 (Domain Component Split Exceptions)
在进行 `scope_level="component"` 的拆分时：
- **必须拆分**：包含复杂方法、需要人工实现逻辑的 `aggregate`, `entity`, `domain_service`。
- **免拆分例外 (Auto-generated/Interface only)**：
  - 简单的 `value_object`, `enum`, `domain_event`, `domain_exception`，如果没有自定义方法及复杂的 `rules`，**不需要**创建子任务，由骨架生成器自动接管。
  - `domain_port` 和 `repository` 在 Domain 层仅作为纯接口存在，不做具体实现，**不需要**拆分 Component 任务。