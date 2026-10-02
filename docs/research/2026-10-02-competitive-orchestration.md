# PROVE 与可比编排方案：定位、证据与聚焦改进

核验日期：2026-10-02（Asia/Shanghai）。研究对象是 Codex 技能、模型编排和验证工作流，不是模型能力排行榜。源码存在不等于本次运行验证；维护者实测不等于独立复现。

## 结论先行

**目前没有证据证明 PROVE 在同等质量下，比下面的成熟方案普遍更便宜或更快。** Solo、按需并行、模型分层、独立审查、恢复记录都不是独有能力。PROVE 可保留的定位是一个显式调用、低安装负担的 Codex 工作约束层：按任务耦合度选择最少协调，保留写入所有权、需求到真实验收证据的闭环，以及模型/成本证据边界。这个组合是否值得额外上下文，仍须同条件验证，不能当成已证实的竞争优势。

不应为了证明混合模型价值，强迫独立性不足的工作拆分或强迫 Luna 参与。若需要完整项目状态管理、持久团队调度、崩溃恢复或跨模型运行时，优先复用合适的现成方案；不在 Skill 内重新实现它们。

## 方法与证据等级

- A：读取了固定版本的实际源码或官方产品文档；证明实现/契约存在，不证明执行结果。
- B：维护者发布的实验、issue 或结果描述；保留其任务、模型、样本与计量限制。
- C：本地原始执行记录或可重复离线故障复现；只覆盖其候选、输入与运行环境。
- U：本次未取得充分结果。U 不等于该项目没有该能力或从未做过测试。

采用三条并行只读研究线：Codex 原生编排、开发/验证工作流、可审计运行时；再与本地源码和已有真实配对核对。仅用上游一手文档、固定源码、论文和原始记录；没有安装竞品、运行下载代码、调用新增付费 API 或修改全局配置。配置里的默认模型与框架支持的模型分开记录。

## 真正可比的替代方案

| 方案及固定版本 | 质量与协调 | 成本、上下文和时间证据 | 恢复、集成与适用边界 |
| --- | --- | --- | --- |
| 普通 Codex 原生 subagents | 角色可继承或覆盖设置；独立分支才有并行价值 | 最重要的零附加技能基线；不是必然单代理，也不能把其所有子代理视为无效开销 | 无需额外编排安装；简单明确的任务优先保留这条路线。[官方文档](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| da34/codex-orchestrator，`df36074b74048cbca9fc987996a1e70403ec70a2`，MIT | 短入口；简单任务 Direct，独立进展才委派；复用验收证据、风险触发审查 | Pro 配置是 Astra 主代理与 Luna worker；不能因仓库简介文字把实际 worker 说成 Sol。提供 Harbor/Codex 六案例评测入口，子代理用量未知时不能据此算完整费用；未取得足以判定对 PROVE 优势的同条件结果 | 最接近的轻量竞争基线；配置模型不同，测试须区分“同模型策略对比”与“各自默认产品对比”。[入口](https://github.com/da34/codex-orchestrator/blob/df36074b74048cbca9fc987996a1e70403ec70a2/.agents/skills/codex-orchestrator/SKILL.md)、[评测说明](https://github.com/da34/codex-orchestrator/blob/df36074b74048cbca9fc987996a1e70403ec70a2/evals/README.md) |
| Superpowers `v6.4.2` / `8ca22dba9a94f28898bbce59f2537ff4d87c747d`，MIT | Native 执行与 SDD 分开：并非每个小任务都需要完整团队。SDD 每任务一个新 reviewer 同时给 spec/quality 两个 verdict，再做最终审查；不是每任务固定两名 reviewer | PR #2318 自报 Native/SDD 三次实验费用差异，主要为 Claude 与有限 Codex 探索，不能拿来计算 PROVE 收益。轻量规划和 Native 路径值得直接复用，不应只挑其最重模式作靶子 | `task-done` 实际执行检查，失败不写完成记录；有修复次数和进度记录。适合已经选择 spec/plan/review 工作流的用户。[执行](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/executing-plans/SKILL.md)、[SDD](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/SKILL.md)、[维护者实验](https://github.com/obra/superpowers/pull/2318) |
| GSD `open-gsd/gsd-core v1.15.0` / `b10ab3fdeb6274b373859ccd6e99b7e1cf17388e`，MIT | 有 phase research、plan check、verification；也有 fast/quick 路线，不等于永远全流程。动态模型路由默认关闭；Codex 模型参数受运行时 schema 支持约束 | 提供配置/内容缩减机制，但本次未取得相对 PROVE 的完整端到端质量、费用和时间结果 | 当前上游已迁移，旧 `gsd-build/get-shit-done` 归档；支持原生 Codex。HANDOFF/STATE、失败修复和受影响尾段重验比单一 Skill 更适合长期多阶段项目。[Codex 安装](https://github.com/open-gsd/gsd-core/blob/v1.15.0/docs/how-to/install-on-your-runtime.md)、[配置](https://github.com/open-gsd/gsd-core/blob/v1.15.0/docs/CONFIGURATION.md)、[模型设计](https://github.com/open-gsd/gsd-core/blob/v1.15.0/docs/adr/2313-codex-passive-model-posture.md) |
| OMX `v0.21.7` / `1dcf51359f3caeeebfed0bcbeea867ff0838d533`，MIT | 普通请求 Direct；小 Team 限制隐式 fanout。Autopilot 缺 evidence 多为 advisory；Ultragoal 显式 `--strict` 才拒绝缺 gate，仍不等于重跑证据或验证 reviewer 身份 | frontier/standard/spark 当前内置默认均为 Astra，cheap opt-in。完整 Team 用量/预算提案 #3226 被关闭且未实现；#3655 的实测采集/模型比较尚未完成，不能把 fixtures 当成果 | 有 durable Team、mailbox、claim/lease、resume/retry；以 CLI 为主，App 非默认支持面。需要可视化 tmux 团队和持久运行状态时比薄 Skill 更匹配。不要沿用弱化 sandbox 的示例参数。[路由](https://github.com/Yeachan-Heo/oh-my-codex/blob/1dcf51359f3caeeebfed0bcbeea867ff0838d533/docs/ordinary-task-routing.md)、[真实默认](https://github.com/Yeachan-Heo/oh-my-codex/blob/1dcf51359f3caeeebfed0bcbeea867ff0838d533/src/config/models.ts)、[预算缺口](https://github.com/Yeachan-Heo/oh-my-codex/issues/3226#issuecomment-5015975040)、[评测进展](https://github.com/Yeachan-Heo/oh-my-codex/issues/3655) |
| ECC `v2.2.2` / `c70874fae9eb0e5ad0365beb7e2955899fd1d30f`，MIT | 原生 Codex 插件是一组可选技能，不是默认接管所有请求的中央路由器。`model-route.md` 的建议不是 Codex 自动路由实现 | Codex hook 只有 SessionStart；不能把 Claude Stop 成本采集归给 Codex。另有 ECC2 alpha 的真实预算暂停代码，但输入来自 Claude metrics，不证明准确的 Codex 全链路成本上限 | 跨 harness 技能复用、session adapter 很有价值；需要通用开发技能时可直接使用 ECC。隐藏 grader/配对设计可借鉴，但 complex-task 实验明确不支持 Codex provider。[原生插件](https://github.com/affaan-m/ECC/blob/c70874fae9eb0e5ad0365beb7e2955899fd1d30f/.codex-plugin/README.md)、[hooks](https://github.com/affaan-m/ECC/blob/c70874fae9eb0e5ad0365beb7e2955899fd1d30f/hooks/codex-hooks.json)、[ECC2](https://github.com/affaan-m/ECC/blob/c70874fae9eb0e5ad0365beb7e2955899fd1d30f/ecc2/README.md)、[Codex 评测设计](https://github.com/affaan-m/ECC/blob/c70874fae9eb0e5ad0365beb7e2955899fd1d30f/docs/design/context-profile-ai-evaluation.md)、[complex-task 限制](https://github.com/affaan-m/ECC/blob/c70874fae9eb0e5ad0365beb7e2955899fd1d30f/docker/context-profiles/complex-eval/DESIGN.md) |

补充检查了 [joserey7/codex-orchestrator](https://github.com/joserey7/codex-orchestrator/blob/8f559d63a67cac4661f66b10dc1f44db5af4ae8b/plugins/codex-orchestrator/skills/orchestration/SKILL.md) 和 [sol-advisor](https://github.com/DannyMac180/sol-advisor/blob/37b75cad535abdd46531f0227483a8842d045ab8/plugins/sol-advisor/skills/orchestration/SKILL.md)。前者的声明式预算校验不等于真实调度/计费约束；后者 Solo/单辅助的方式也表明“默认少代理”不是 PROVE 独有定位。没有发现足以决定胜负的可比实测包。

## 能借鉴、但不是同层替代的运行时

1. **mini-swe-agent v2.4.6**（MIT，`a83fcae82d2a08f0ee0c688f9d137b3566c097f8`）：在请求前检查 step/cost/wall，响应后记账；修复了已计费解析失败的漏记。一次请求仍可能跨过费用阈值，在途请求和失败无回执的费用不自动变成零。它的独立进程组超时比提示词有更强的运行约束。适合研究/评测或需独立运行环境的任务，不是能原样装进 Codex 的路由 Skill。[agent 实现](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/agents/default.py)、[模型计量](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/models/litellm_model.py)。SWE-agent 的不同计数层还提示：chooser 的预算未必包括 selection reviewer，工具时间也不等于端到端 wall time。[reviewer 实现](https://github.com/SWE-agent/SWE-agent/blob/0f3acafacabc0def8cc76b4e48acb4b6cf302cb9/sweagent/agent/reviewer.py)。
2. **LangGraph 1.2.12**（MIT，`49cce0ca852be4cfb567a1cbe0e511ff325a1682`）：checkpoint/pending writes 是真实持久状态，但外部副作用不自动回滚或 exactly-once；恢复可能从 node 开头重跑，需幂等动作或外部状态核对。recursion limit 不是美元/LLM-call 硬预算，且可按 invocation 重置。需要真正持久恢复与人工中断时，应考虑这类运行时，不让一个 resume 文本冒充同等保证。[persistence](https://docs.langchain.com/oss/python/langgraph/persistence)、[interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)、[fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance)。

以上工程是能力边界参考，不进行跨基准排名。SWE-bench 的多任务并发，不等于同一个任务内多代理获益；taubench 的 supervisor/swarm 结果也不能直接移植为 Codex 改仓库的结论。

## 研究能支持什么，不能支持什么

- [OpenAI subagents 文档](https://learn.chatgpt.com/docs/agent-configuration/subagents)支持“默认继承、角色可覆盖、以实际运行时为准”；TOML、启动选择、实际执行元数据、提供方计费回执是不同证据层。PROVE 现有候选已区分这些层，不另加身份握手或全历史扫描。
- [OpenAI 的 skill/prompt 指引](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)支持精简入口和按需加载参考资料；不支持用一次 token 减少证明通用收益。
- [Towards a Science of Scaling Agent Systems，v3（2026-04-08）](https://arxiv.org/html/2512.08296v3)提示任务耦合、单代理能力和工具开销影响多代理收益；其有限 coding cells 和跨模型结果不应变成 PROVE 的硬阈值或当前模型预测。
- [Anthropic 多代理研究系统经验](https://www.anthropic.com/engineering/multi-agent-research-system)针对可并行研究；内部提升和相对 chat 的 token 倍数不是同模型 Codex coding 对照。
- [OpenCollab 预印本（2026-09-29）](https://arxiv.org/html/2609.38345v1)提示声明的组织方式与实际遵从有差异。新预印本不是 PROVE 优势证据，也不据其表格许诺质量/价格/速度同时占优。

## 本地证据与真实缺口

已独立核对上一冻结候选 `38ce7bdd…` 的一个真实项目修正版配对：两组共同任务与项目起点相同，候选运行时未漂移，进程串行、退出 0；逐会话最终累计计数未重复加入快照。基线 root + 1 worker；PROVE 为 Host Solo。两组独立 oracle 都是 11/11；PROVE 没有因此完成混合模型路线验证。

| 指标 | 普通 Codex | PROVE Solo |
| --- | ---: | ---: |
| 完整执行树 total tokens | 2,071,501 | 935,288 |
| 其中 cached input | 1,895,168 | 814,336 |
| 端到端秒数 | 589.609 | 630.721 |
| 固定费率 API 等价估算 USD | 0.7018068 | 0.4546096 |

单对样本的 token 为 -54.85%，API 等价估算为 -35.22%，用时为 +6.97%。估算按每百万 input/cached input/output = 2/0.1/10 USD、请求上下文均低于长上下文界限；[官方价格](https://developers.openai.com/api/docs/pricing)。它不是实际订阅账单、额度节省或竞品对照，实验外共同审计成本也未计入上述执行树。原始项目产物/rollout 属于本地实验，不复制入公开仓库。报告所写快照 753 文件应为实际 749；两组相同，不改变配对关系。

现有策略已经覆盖按耦合度选 Solo、Host 承担有用工作、条件式 Astra、Luna 的机械边界、唯一 writer、按变化复验和保留重试历史。这次不重写这些已存在规则。

**已复现并修复的离线缺口：** 改动前 `tests/worker_model_pilot.py::parse_usage` 将同一 thread/turn 的两条相同 `turn.completed` 从 input=100 加成 200；成功事件后又有失败，仍返回看似完整的用量；`run_skill_probe.py` 允许子代理但没有给这个数字标明 root-only 范围。前述真实配对采用逐 session 的另一套人工核对，不受这个开发探针缺陷追溯影响。

新解析器在两份未修改的真实 CLI 日志上重放：基线 root 输入 1,280,012，PROVE root 输入 918,879；两者均只标 `root_cli_stream_only`，`whole_run_usage=null`。基线含子代理的全树输入实际为 2,051,548，正说明不能把 root 结果当成全程。失败/超时后的已知成功子集放在 `observed_completed_usage`，不再返回看似完整的 `usage`。

## Adopt / adapt / reject

| 决定 | 内容 | 这轮落点 |
| --- | --- | --- |
| Adopt | 同一输入、同一验收、失败保留分母、未知用量不当零；最轻的合理竞品模式也要入选 | 保持现有 A/B 合同；补齐开发探针重复、冲突、失败、scope 检查 |
| Adapt | 成熟运行时对 budget、checkpoint 的真实边界 | 仅补文档契约：声明预算覆盖范围/执行强度；恢复先核对未知外部动作，不承诺硬预算或 exactly-once |
| Adapt | 风险在批量扩散前暴露，而非盲目廉价重试 | Luna 仅在规则或检查器未经验证、输入异质时先检查代表项；已有可信规则不强制增加步骤/模型调用 |
| Retain | Solo、独立性、最小交接、selected/observed 身份、一次最终验收 | 已实现；没有新证据要求换模型、增加角色或常驻日志 |
| Reject | 固定模型配额、固定团队人数、通用复杂度分值、廉价模型必须先失败 | 没有跨任务测量依据，可能损害质量和时间 |
| Reject | 在 Skill 内自建 durable scheduler、数据库 checkpoint、hook 计费系统 | 与本次范围不符；有真实需求时评估 OMX/GSD/LangGraph/独立 runner |
| Reject | 本次把 full-run collector 或现金硬上限包装成已实现能力 | root CLI 结果只能据实标范围；完整树仍须保留每个 session 原始记录并核对子代理发现与失败覆盖 |

## 可测目标与下一次真实项目验收

本轮实现目标是计量正确性和边界清晰，不以未经运行的成本/速度收益作验收。

1. 重复相同身份只计一次；冲突、无法区分的多条完成、非法计数、截断、未完成 turn 或失败缺口不得返回完整 totals；已知成功部分可单列，不能冒充全部。子代理不因 root JSON 有数字就自动被计入。
2. 不改变四个角色的模型、effort、权限或调用方式；入口不增加常驻步骤；新策略细节留在已有按需参考。没有硬预算执行器时不得声称硬上限已保证。
3. 新增离线行为回归、运行完整现有回归和源码/安装只读验证；保留旧实验与旧冻结包。离线解析测试不冒充真实模型路由测试。
4. 冻结新候选后，沿用已有真实测试会话，在用户授权的项目中选尚未完成、可独立验收的实际任务；不要把此前答案回灌起点。普通 Codex 与 PROVE 共用任务、起点、权限、模型选择可见性与独立 oracle，顺序交错或明确注明顺序偏差。保留失败/超时/重试，报告所有 session 的实际模型、token、缓存、费用未知项和端到端时间。
5. 若要回答“为什么不用竞品”，下一条有代表性的可比任务加入 **da34 最小编排**；若任务主要是规格/计划驱动，选 **Superpowers Native** 而非强行套最重 SDD。先核对版本许可和受支持的原生集成，不改全局安装。控制为一个代表任务，不开展无边界 benchmark。

质量门槛：独立 REQ 检查与写入边界不能退步；成本和时间分别报告变化，不用合成分数掩盖 trade-off。预先把 ≥10% 的全树 token/API 等价费用或 wall-time 差异作为值得复测的信号，而非单次胜负定论；n=1 只出案例结论，稳定优势至少需要不同任务/重复观测支持。没有完整费用证据时只比较有覆盖的原始用量，并明确 unknown。

## 什么时候值得选择 PROVE

这是基于功能匹配的建议，不是性能胜出声明：已有 Codex 工作环境、希望显式启用少量分工且重视候选/证据/所有权边界时，可以试用薄层 PROVE 并保留普通 Codex 基线。短小任务直接用 Codex；偏长期 phase 管理选 GSD；偏持久 CLI Team 选 OMX；偏跨 harness 技能库选 ECC；偏强 spec/plan/review 习惯可选 Superpowers；偏真正持久程序状态与外部动作恢复则评估现成运行时。

如果新的真实对照不能体现更好的功能匹配或可重复收益，应该缩减或复用 PROVE 中有价值的约束，而不是要求用户仅因自建项目就选择它。

## 本轮实现与验证记录

- 仅在既有 orchestration 参考补充 Luna 条件式代表项检查、未知副作用恢复和预算执行强度；109 行主入口和四角色配置不变，未加入调度器、hook、默认模型调用或全会话扫描。
- 修复原有解析器并让 probe/legacy pilot 传入真实进程完成状态；补全 scope、未知项、去重和成功子集，未制造完整成本采集能力。
- 新增 15 项离线测试；最终完整回归 163/163，计量/旧实验专项 29/29，启动器 9/9。首次故障回归在旧实现上出现实际重复累计和未知缺口错误，修复后通过；并非只检查字段拼写。
- 两份真实保存日志只读重放通过、字节哈希不变；源码/安装只读检查和四套既有配图事实验证通过。未重跑旧项目测试或模型，也未进行新的竞品 A/B；新策略的实际路由收益待新冻结候选的真实项目验证。
- PowerShell 不在本机可用范围，Windows 保持结构验证边界。首次直接用系统 Python 跑 suite 因缺少 `tomllib` 未执行用例，改用项目脚本选择的 Python 3.13 后完成上述验证；没有安装依赖来掩盖环境差异。
