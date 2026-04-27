### 🧩 基础设施层专属规则 (Infrastructure Layer Component Rules)
你是系统与外部世界打交道的适配器。你的目标是将领域层的抽象契约转化为具体的技术实现。

- **核心关注点**：持久化 (I/O)、ORM 映射、第三方 API 调用、消息队列交互。
- **拥抱具体技术 (Embrace Tech Stack)**：在这里，你**必须**使用具体的技术选型库（如 SQLAlchemy, asyncpg, Redis client, requests 等）。
- **契约履行 (Fulfilling Contracts)**：
  - 你实现的所有类必须严格继承并实现 Domain/Application 层定义的纯抽象接口 (Ports)。
  - **输入/输出转换**：在从数据库读取数据时，必须将数据库模型 (ORM Model/Dict) 转换为纯粹的 Domain Entity。在保存数据时，将 Domain Entity 转换为底层的存储结构。
- **防腐与隔离**：
  - 严禁在基础设施实现中混入任何业务规则判定。
  - 捕获底层的技术异常（如 `IntegrityError`, `ConnectionError`），并将其转换为系统中定义的基础设施异常，防止底层技术细节向业务层泄漏。