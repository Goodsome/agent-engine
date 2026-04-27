### 🧩 接口层专属规则 (Interfaces Layer Component Rules)
你是系统的边界门户。你的目标是解析外部输入，并将其转化为系统可理解的内部指令。

- **核心关注点**：请求路由、参数解析与校验、协议适配 (HTTP/gRPC/CLI)、响应格式化。
- **通信协议感知**：你是唯一可以处理 HTTP Request/Response, URL 路径参数, 状态码 (如 200, 400, 404), 或 CLI 参数的层级。
- **严格向下调用**：
  - 你只能调用 Application 层 (UseCases/Handlers) 的服务。
  - **绝对禁令**：严禁绕过 Application 层直接调用 Domain 层的业务对象或 Infrastructure 层的数据库操作。
- **数据进出规范**：
  - **入站**：使用 Pydantic 或框架自带的 Schema 校验外部数据的合法性与类型，然后将其组装为 Application 层的 Command/Query 对象。
  - **出站**：接收 Application 层返回的 DTO，并将其序列化为最终响应格式（如 JSON）。
  - **异常映射**：捕获底层的 `DomainException`，并将其映射为合适的呈现层状态（例如，将 `ChannelNotFoundError` 映射为 HTTP 404，将业务校验失败映射为 HTTP 400）。