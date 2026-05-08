### 🔌 接口层专属建模准则 (Interfaces Architecture Rules)
你当前处于六边形架构的最外环（接口层）。你的核心职责是将外部协议（HTTP/CLI/gRPC）的请求转化为系统可理解的内部指令，并将内部结果序列化为外部响应。**严禁**在本层包含任何业务逻辑或领域规则。

#### 1. 接口层组件元模型规范
在修改 `codegen.yaml` 的 `interfaces` 节点时，必须严格遵循以下组件的职责约束：
- **Endpoint (端点)**：对外暴露的协议入口（如 HTTP 路由、CLI 命令）。负责接收外部请求，调用 Application 层用例，并返回格式化响应。
- **Request Schema (请求模型)**：入站数据的校验与解析模型（通常使用 Pydantic）。负责将外部原始数据转化为强类型的内部对象。
- **Response Schema (响应模型)**：出站数据的序列化模型。负责将 Application 层返回的 DTO 转化为外部协议所需的格式。
- **Error Handler (异常处理器)**：捕获底层异常并映射为协议层可理解的状态（如 HTTP 状态码、CLI 退出码）。
- **Middleware / Interceptor (中间件/拦截器)**：横切关注点的处理（如认证、日志、限流）。

#### 2. 协议适配约束 (Protocol Adaptation)
- **HTTP 端点**：必须定义 HTTP Method、路径、状态码映射。成功返回 2xx，客户端错误返回 4xx，服务端错误返回 5xx。
- **CLI 端点**：必须定义命令名称、参数解析规则、退出码映射。
- **唯一协议感知层**：接口层是系统中唯一可以处理 HTTP 头信息、URL 路径参数、状态码、或 CLI 参数的层级。

#### 3. 异常映射规范 (Exception Mapping)
接口层必须将底层异常映射为协议层友好的响应：
- `DomainException` → 业务校验失败 → HTTP 400 / CLI Exit Code 2
- `NotFoundException` → 资源不存在 → HTTP 404 / CLI Exit Code 3
- `UnauthorizedException` → 权限不足 → HTTP 401 / CLI Exit Code 4
- 未捕获异常 → 系统内部错误 → HTTP 500 / CLI Exit Code 1

#### 4. 接口层子任务拆分准则 (Interfaces Component Split)
在进行 `scope_level="component"` 的拆分时：
- **必须拆分**：包含复杂路由逻辑、多条件异常映射、或需要人工实现协议适配的 `endpoint`。
- **免拆分例外 (Auto-generated)**：
  - 简单的 `request_schema`、`response_schema`，如果没有自定义校验规则或复杂的字段转换，**不需要**创建子任务，由骨架生成器自动接管。
  - 纯数据模型通常无需人工干预。
