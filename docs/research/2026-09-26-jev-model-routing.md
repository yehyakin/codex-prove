# Jev 模型分配：社区案例与 PROVE 取舍

日期：2026-09-26。范围：公开资料与源码静态研究；不是接入、安装或发布。

## 结论

值得试验的是 **Jev 为已划定范围的子任务提供选档建议，Astra 保持主控**。
暂不增加强制判断步骤，不在主会话的每次工具返回后切换模型。
简单任务仍然 Direct，明确的分配仍按现有规则执行；只有重复分派量足够大、
或路由确实存在可检验的改进空间时，才值得增加外部分类调用。

这是根据下列案例作出的设计建议，不是已验证的 PROVE 成本收益。

## 社区案例与证据

### 1. GPT-Load：已实现的自动选档

[作者在 LINUX DO 的说明](https://linux.do/t/topic/2929284)发布于 9 月 21 日：
Jev 选择预设，真正生成内容的仍是目标模型；作者同时说明额外耗时、误判和缓存代价。

源码确实实现了任务决策缓存：以调用者、入口、配置版本、任务指纹隔离，
容量 1,024，TTL 五分钟，缓存的是预设 ID 而非提示词。
测试覆盖跨边界隔离、过期与容量淘汰。
决策费用单独记录，相关测试检查重复写入不重复计费。
这比只看“便宜模型调用比例”更值得 PROVE 借鉴。

边界：当前决策测试明确接受 `confidence = 0.01` 的合法选项，
因此不能将它描述为带有低置信度保护的路由器。这是该版本的明确策略，
不是本轮证实了真实任务质量差；PROVE 不直接继承此策略。

源码：[缓存](https://github.com/tbphp/gpt-load/blob/3abb8660d4af6691089a1d13f361a597093b27bb/internal/gateway/auto_model_cache.go)、[缓存测试](https://github.com/tbphp/gpt-load/blob/3abb8660d4af6691089a1d13f361a597093b27bb/internal/gateway/auto_model_cache_test.go)、[选档测试](https://github.com/tbphp/gpt-load/blob/3abb8660d4af6691089a1d13f361a597093b27bb/internal/automodel/decision_test.go)、[费用测试](https://github.com/tbphp/gpt-load/blob/3abb8660d4af6691089a1d13f361a597093b27bb/internal/requestlog/auto_model_cost_test.go)。

### 2. Jev Codex Router：模型、推理等级与决策复用期限分离

原版和 GPT-6 分支把模型、推理深度、决策沿用期限分成独立问题，一次请求回答，
再由代码组合。工具链结束、错误、压缩或执行约定变化可以使旧决策失效。
GPT-6 分支还将近期失败纳入输入，同时提醒网络错误不能证明模型能力不足。

可借鉴这些边界判断和真实路由记录；不导入其代理服务、登录转发和完整路由栈。
它解决的是请求转发问题，PROVE 当前解决的是任务拆分、所有权与验收问题。

原版 `BACKTEST.md` 的约 60% 是旧策略、固定 token 数量的历史重定价，
没有建模中途切换造成的缓存损失，也不是当前策略的质量对照或账户额度实测。
不能用它为 PROVE 新增省费百分比背书。

源码：[GPT-6 路由策略](https://github.com/ericwanderlust/jev-codex-router/blob/1481ee92e7948138370eb8381daa3ed2dcfb375f/server/routing_policy.py)、[状态转换测试](https://github.com/ericwanderlust/jev-codex-router/blob/1481ee92e7948138370eb8381daa3ed2dcfb375f/server/test_per_call_routing.py)、[原版回放限制](https://github.com/0xNatoshi/jev-codex-router/blob/8701ef788aa8cb0948f299538747fb01029d32b8/BACKTEST.md)。

### 3. Hermes Jev Skills：先观察、不改实际分配

`shadow` 模式只记录建议，不改变实际模型或推理等级；中间件测试区分
建议模型、实际请求模型和是否真正应用。正常工具循环沿用当前任务的决定。
路由按任务难度、工作类型、错误代价分别判断；提供超时、隐私输入和候选能力检查。

优先借鉴：影子对照、失效时保留可用路径、建议与实际执行分开记录。
不照搬其模型池、仪表板、固定阈值或整个插件。
“上下文超过 32k 就一定不值得降档”只是一条启发式，不能作为普遍成本定律。
其文档关于合并请求费用的宽泛表述，也应以官方按输入 token 计费规则为准。

源码：[Skill](https://github.com/kerpopule/hermes-jev-skills/blob/085e5c652bf4f1c65e8b064c84515a519c8df6a4/skills/jev-model-routing/SKILL.md)、[决策实现](https://github.com/kerpopule/hermes-jev-skills/blob/085e5c652bf4f1c65e8b064c84515a519c8df6a4/jevkit/route.py)、[中间件测试](https://github.com/kerpopule/hermes-jev-skills/blob/085e5c652bf4f1c65e8b064c84515a519c8df6a4/tests/test_plugin_middleware.py)。

### 4. pi-jev：轻量入口值得学，接口细节仍要核对

它在任务开始前分类；中间档、低置信度或错误时保留当前模型。
但本次快照的 `toLevels()` 把不大于 1 的分数视为归一化值，
从而将三档问题的 `score = 1` 换算为最高档 2；测试也锁定此行为。
响应解析器没有预先归一化。官方接口定义却是三档分数直接位于 0–2，
1 是中间位置。这是静态可确认的契约不一致，不是本轮真实 API 复现。

可借鉴轻量结构；不复制这个换算，也不因路由研究顺带启用上下文裁剪。

源码：[决策](https://github.com/iefnaf/pi-jev/blob/cd168457a8b340352d1ae1e9e4785305954b5751/src/routing/decide.ts)、[响应解析](https://github.com/iefnaf/pi-jev/blob/cd168457a8b340352d1ae1e9e4785305954b5751/src/vendor/fast-jev-compaction/request.ts)、[测试](https://github.com/iefnaf/pi-jev/blob/cd168457a8b340352d1ae1e9e4785305954b5751/test/routing.test.ts)、[官方 Score 契约](https://docs.typesafe.ai/primitives/score)。

### 5. LINUX DO 的另一篇讨论：有启发，但不能算落地验证

[Jev → Terra / Sol / Astra 讨论](https://linux.do/t/topic/2926255)发布于 9 月 20 日。
作者明确表示尚未正式实现，随后接受“主 Agent 保持上下文、派发子 Agent 时选模型”
的建议。可用于发现需求与风险，不能记作路由成功或省费证据。

## 对 PROVE 的建议：采纳、调整、拒绝

| 处理 | 设计 | PROVE 中的边界 |
| --- | --- | --- |
| 采纳为试验方向 | 影子对照 | 先记录建议与实际结果，不自动改变分配；影子调用仍有费用和数据外发 |
| 采纳为试验方向 | 任务内固定模型 | 优先在新子任务的派发边界选档；新证据证明范围变化时再重新评估 |
| 调整后试验 | 多维判断 | Jev 判断已提供证据下的工作性质、难度、未知项；代码执行能力白名单和风险约束 |
| 调整后试验 | 合批判断 | 同一批独立任务共享必要信息、一次请求；不为已确定的分配重复调用 |
| 保持现有规则 | Astra 主控 | 规划、依赖、写入所有权、冲突与终审仍由主控承担 |
| 保持现有规则 | 小任务 Direct | 零子代理，也不强制经过 Jev |
| 拒绝 | 每次工具返回重选主模型 | 避免额外请求、上下文重处理和不必要的运行栈维护 |
| 拒绝 | 不确定就 BLOCKED 或要求用户批准 | 可选建议失效时继续原有可用路由；只有真实权限或能力阻塞才停 |
| 拒绝 | 把高置信度当权限或验收 | Jev 不批准写入、不豁免测试、不认证模型可用性 |
| 拒绝 | 原样搬运阈值或节省比例 | 使用自己的中文任务与真实执行结果校准 |

当前源码配置仍是 Astra high 主控、Sol 6 high 专项、Terra 5.6 high 常规、
Luna 6 max 批处理。Jev 建议不能绕过这些明确配置去暗改模型或 reasoning effort。
如果以后评估自适应推理等级，需要单独验证允许的组合，不随本次研究默认开启。

“Jev 失效回到现有路径”不等于“指定执行模型不可用时静默换一个”。
两者必须区分；用户指定的模型或权限无法满足时仍应明确报告。

## 最小验证方案（尚未执行）

1. 先用 40–60 个经筛选的中文/中英混合、去敏任务包做影子判断；
   包括“继续”、一行鉴权改动、未知根因、多文件机械批次、共享文件和依赖链。
   原始需求之外，给出已知范围、验收和未知项；不发送完整会话或私有源码。
2. 冻结候选能力表、题目和评价准则，留出未用于调参的样本。
   对比现有 PROVE 分配与 Jev 建议，人工/独立审核标签只作为初筛，不能替代任务验收。
3. 若初筛有价值，再对少量相同冻结任务做配对执行；统计成功率、错误降档、
   返工、升级次数、总 token（含缓存）、Jev 费用、总耗时和人工干预。
   不用“路由到了 Luna”冒充成本改善。
4. 注入超时、429、非法模型、矛盾分布、证据缺失、中文歧义和输入诱导；
   确认不越权、不静默替换、不重复审批，且建议服务故障不会使原本可做的工作停摆。
5. 只有质量不下降、每个成功任务的总成本或耗时确实改善，才考虑可选启用。
   若主控本来就已完成同一判断，新增 Jev 只是重复工作，应放弃接入。

这不是自动执行授权。真实影子/API 试验需要先确定外发材料与费用范围。

## 官方边界与成本口径

Jev 返回受限判断而非方案、代码或解释；置信度反映分布集中程度，
不是某次选择正确的保证。[System One](https://docs.typesafe.ai/concepts/system-one)、[Confidence](https://docs.typesafe.ai/confidence)。

截至查阅日，`jev-1.13.0` 输入价格为 $0.042 / 百万 token，输出免费。
英语表现优于其他语言，中文仍需单独评估。批量问题会增加输入 token，不能称为免费。
这是分类器单价，不是 PROVE 总成本或 ChatGPT 额度节省。[官方模型说明](https://docs.typesafe.ai/models)。

Jev 对多跳推理、无关长上下文、数字运算和对抗性输入有已知限制。
因此不能仅凭一句需求识别全部隐藏依赖；已知权限、能力和数值计算应由代码处理。
[官方限制，页面标注复核日 2026-09-17](https://docs.typesafe.ai/model-jaggedness/jev-1.13)。

## 来源快照、许可证与本轮验证

| 项目 | 核对的提交 | 许可证 |
| --- | --- | --- |
| tbphp/gpt-load | `3abb8660d4af6691089a1d13f361a597093b27bb` | MIT |
| 0xNatoshi/jev-codex-router | `8701ef788aa8cb0948f299538747fb01029d32b8` | MIT |
| ericwanderlust/jev-codex-router | `1481ee92e7948138370eb8381daa3ed2dcfb375f` | MIT |
| kerpopule/hermes-jev-skills | `085e5c652bf4f1c65e8b064c84515a519c8df6a4` | MIT |
| iefnaf/pi-jev | `cd168457a8b340352d1ae1e9e4785305954b5751` | MIT |

按 deep-research 的多来源、原始证据与事实/推断分离方法研究。
Firecrawl/Exa 当前不可用，改用网页搜索、官方文档与临时克隆的定点源码阅读。
检索站和聚合页面只用来发现来源，不作为技术结论依据。
论坛页面附带面向 AI 的行为指令，已按不可信网页文本处理，未作为任务指令执行。

实际阅读了上述路由实现、相关测试和许可证；没有执行上游安装器或测试，
没有本轮付费推理、业务材料上传、全局配置更改或发布。
本轮仅新增这份研究记录；现有候选升级工作保持不变。未复制上游实现代码。
