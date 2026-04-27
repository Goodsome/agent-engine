### 🧩 领域层专属规则 (Domain Layer Component Rules)
你是系统的心脏。你的目标是实现纯粹的业务逻辑与状态转移。

- **核心关注点**：业务不变量 (Invariants)、充血模型、状态变更、业务校验。
- **绝对纯洁性 (Absolute Purity)**：你的代码必须是纯粹的 Python 对象。**严禁**引入任何与框架、数据库 (SQL/ORM)、网络 (HTTP/gRPC) 或底层 I/O 相关的依赖库。
- **状态变更规范 (Aggregates & Entities)**：
  - 严禁通过直接赋值 (setter) 修改核心属性。所有状态变更必须通过具有明确业务意图的方法进行。
  - 在修改状态前，必须严格校验业务前置条件（基于 YAML 中定义的 `rules`）。
  - 若违反业务规则，必须抛出该上下文专属的 `DomainException`，严禁抛出通用的 `ValueError` 或 `Exception`。
- **不可变性 (Value Objects)**：值对象一旦初始化，其属性必须是绝对不可变的 (`frozen=True`)。
- **依赖倒置 (Dependency Inversion)**：如果领域逻辑需要外部信息，必须依赖并调用 `Domain Port` (纯接口)，绝不关心其具体实现。
