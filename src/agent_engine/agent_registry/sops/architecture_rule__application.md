### 🧩 应用层专属建模准则 (Application Architecture Rules)
你当前处于六边形架构的中间环（应用层）。你的核心职责是编排领域对象与基础设施端口，完成一次完整的业务用例。**严禁**在本层引入任何核心业务规则的计算逻辑。

#### 1. 应用层组件元模型规范
在修改 `codegen.yaml` 的 `application` 节点时，必须严格遵循以下组件的职责约束：
- **Use Case (用例)**：一次完整的业务操作编排。接收 Command/Query，协调领域对象与基础设施，返回 DTO。是应用层的核心构建块。
- **Command / Query (命令/查询)**：不可变的输入指令对象，封装用例所需的全部参数。Command 表示写操作，Query 表示读操作。
- **DTO (数据传输对象)**：用例的输出载体，面向接口层的扁平数据结构。**严禁**将领域实体或聚合根直接暴露给上游。
- **Application Service (应用服务)**：当用例逻辑较轻或需要跨用例共享的编排逻辑时使用。
- **Application Exception (应用异常)**：用例执行过程中产生的非领域级异常（如资源未找到、权限不足）。

#### 2. 应用层子任务拆分准则 (Application Component Split)
在进行 `scope_level="component"` 的拆分时：
- **必须拆分**：包含复杂编排逻辑、多步骤事务协调、或需要人工实现业务流程的 `use_case`。
- **横切关注点 (Cross-Cutting Concerns)**：以下组件涉及应用层的装配与集成，必须单独拆分为子任务：
  - **Container 依赖注入配置**：在 DI 容器中注册 Use Case、Application Service 及其依赖（Repository、EventPublisher 等），确保依赖关系正确绑定。
  - **事件注册与绑定**：配置 Domain Event 的订阅关系，将事件处理器（Handler）与对应的事件类型绑定，确保事件驱动流程畅通。
- **免拆分例外 (Auto-generated)**：
  - 简单的 `command`、`query`、`dto`，如果没有自定义校验逻辑或复杂的转换规则，**不需要**创建子任务，由骨架生成器自动接管。
  - 纯数据载体对象通常无需人工干预。
