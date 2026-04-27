## BDD Generation Rules (核心生成规则)

### 1. 明确初始状态 (Definitive States in `Given`)
* **严禁**使用模糊描述（例如："A new entity" 或 "A valid user"）。
* **必须**指出具体的关键属性和状态。
  * *正确示例：* `Given an EventType with versions=[] (empty list) and a new SchemaVersion with status=DRAFT`

### 2. 精确触发动作 (Precise Actions in `When`)
* **必须**明确指出调用的方法名以及传入的关键参数特征。
  * *正确示例：* `When add_version() is called with this new version`

### 3. 可观测的断言 (Observable Outcomes in `Then`)
* **严禁**使用模糊的业务结果（例如："It should be successful" 或 "It fails"）。
* **成功场景：** **必须**指出状态的具体变更。
  * *正确示例：* `Then the system must automatically transition the new version's status to ACTIVE`
* **失败场景：** **必须**指出抛出的具体异常类型或包含的错误信息。
  * *正确示例：* `Then it must raise SchemaIncompatibleException`

### 4. 强制边界覆盖 (Mandatory Edge Case Coverage)
* 针对每个核心行为，除了提供 1 个 Happy Path（理想路径）外，你**必须**至少生成 1-2 个 Edge Cases（边界异常情况）。
* *常见边界包括：* 状态机非法流转、兼容性模式冲突、必填参数为空、违反业务不变量等。

---

## Output Format (输出格式要求)
请使用标准的 Gherkin 语法 (`Scenario`, `Given`, `When`, `Then`) 输出，并为每个场景提供清晰的标题说明其测试意图。