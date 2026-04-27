### 🧩 应用层专属规则 (Application Layer Component Rules)
你是业务用例的编排者。你的目标是协调领域对象与基础设施，完成一次完整的用户请求。

- **核心关注点**：用例编排、事务管理、权限校验、DTO (Data Transfer Object) 转换。
- **严禁包含领域逻辑**：你只负责“调度”，不负责“计算”。你不能包含任何核心的业务规则校验（那是 Domain 的事）。
- **标准工作流 (Standard Workflow)**：
  1. 接收输入指令 (Command/Query)。
  2. 通过基础设施层 (Repository) 加载聚合根/实体。
  3. 调用聚合根/实体上的领域方法执行业务行为。
  4. 将状态变更通过 Repository 保存。
  5. 触发并发布 Domain Events（如有必要）。
  6. 返回扁平的 DTO 对象给接口层。
- **边界隔离**：
  - **向下**：只能通过 Domain 层定义的接口（Ports/Repositories）与外部设施交互。
  - **向上**：严禁在你的代码中处理 HTTP 状态码、请求头或 CLI 参数。