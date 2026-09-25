# 2026-09-25：同类编排实现复核与常规 worker 对照

状态：开发分支研究，不是发布公告。目标是减少重复劳动与误阻塞，不增加固定团队、
必经审核或运行时台账。本轮延续 `codex/gpt6-lean-v1.1`，保留此前候选改动。

## 来源、许可和实际检查范围

只读取得以下公开快照；没有安装或运行上游插件、Hook 或有权限副作用的基准命令。
这些是可检查的设计参考，不按 star 数或 README 宣传给它们质量排名。
本轮只借鉴思想和测试方法，新增文字与测试独立实现，没有复制上游实质代码或文案。
此前改写 Ponytail 指导的 MIT 许可仍随 Skill 安装，本轮不删除或替换它。

| 来源与固定提交 | 许可 | 检查的实际文件 |
| --- | --- | --- |
| [da34/codex-orchestrator](https://github.com/da34/codex-orchestrator/tree/df36074b74048cbca9fc987996a1e70403ec70a2) · 2026-09-11 | MIT，da34 | `.agents/skills/codex-orchestrator/SKILL.md`、`.codex/agents/worker.toml`、`evals/README.md`、`evals/report.py`、`evals/test_bench.py` |
| [joserey7/codex-orchestrator](https://github.com/joserey7/codex-orchestrator/tree/8f559d63a67cac4661f66b10dc1f44db5af4ae8b) · 2026-09-09 | MIT，Daniel McAteer | `plugins/codex-orchestrator/skills/orchestration/SKILL.md`、其 `references/evaluation.md`、`scripts/task_state.py` 的状态/审核校验、`tests/test_task_state.py` |
| [DannyMac180/sol-advisor](https://github.com/DannyMac180/sol-advisor/tree/37b75cad535abdd46531f0227483a8842d045ab8) · 2026-08-16 | MIT，Daniel McAteer | `plugins/sol-advisor/skills/orchestration/SKILL.md`、`agents/sol-advisor-sol-reviewer.toml`、`scripts/verify.sh` 的校验与迁移夹具 |
| [obra/superpowers](https://github.com/obra/superpowers/tree/5bf4e78011075bcfc0dc295f0724994cd123ee71) · 2026-09-18 | MIT，Jesse Vincent | `skills/subagent-driven-development/SKILL.md` 的任务、审核与恢复段落；`docs/testing.md` 对静态测试和真实会话 eval 的区分 |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail/tree/e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156) · 2026-09-14 | MIT，DietrichGebert | `skills/ponytail/SKILL.md`、`benchmarks/agentic/README.md`；与此前已适配的最小实现原则比较 |
| [joaquinhuigomez/agent-eval](https://github.com/joaquinhuigomez/agent-eval/tree/6d062a2f5cda6ea443bf5d458d361892c04e749b) · 2026-03-16 | MIT，Joaquin | `src/agenteval/runner.py`、`judge.py`、`tests/test_judge.py`；检查隔离、重复与判分方式 |

日期为相应提交时间，不意味着每个文件当日修改；表中列出的是阅读范围，不代表我们
运行过上游测试或认证过它们全部能力。参考原始文件，不把搜索摘要中的模型名称当作配置。

## 吸收、调整、拒绝

| 发现 | 决定及落点 |
| --- | --- |
| da34 以独立进展、上下文隔离等实际收益决定是否委派；主线程不重复 worker 的工作 | 吸收。补入编排 reference；文件多、模型可用不是委派理由，同规则修改合批。 |
| da34 的 grader 校准、缺失 reward 不算成功，缺失统计保留空值 | 吸收到开发期评测：先验证已知错误版本失败、参考实现通过，再运行付费模型；没有额度数据就不计算额度节省。 |
| joserey7 把执行难度与失败后果分开，当前 revision 必须有真实验收 | 保留 PROVE 已有 candidate-bound 证据；补充小改也可能高风险。拒绝全任务强制新 reviewer、常态预算台账和新增模式开关。 |
| Sol Advisor 当前正文以 solo 为默认，delegate/audit/full 按需选择，辅助调用应替代而非重复主线程工作 | 与我们的减法方向一致，不照搬其自证/确认前置。没有子代理隐藏元数据不是要求用户再批准的理由。 |
| Superpowers 强调任务包、同类修改合批、可恢复状态和按已知问题复审 | 保留这些思想；拒绝每个任务双审核、固定多轮修正、所有实现串行和常驻计划台账。它也明确“能描述技能”不等于“实际行为正确”。 |
| Ponytail 用真实 agent、隔离输入、功能完整性和对抗用例检验精简 | 保留复用已有 helper；测试不是冗余。拒绝只优化 LOC、默认全局 Hook、额外持久模式。上游性能数据不迁移为 PROVE 的收益。 |
| agent-eval 的重复试验和隔离有价值，但所读 `judge.py` 在无测试或尚未实现的 LLM judge 分支返回成功 | 只借鉴实验设计，不安装该 runner，也不采用默认 PASS。判分必须执行实际确定性检查；未知不是成功。 |

这些改动不增加 Agent、不增加 packet 必填字段，不改变授权边界。Skill 入口保持不变，
细节只补在按需加载的 reference。等待容量是排队，不是工作失败；事件等待和用户进度
更新分开，主线程不因等待而抢占仍在写入的 worker。

## 模型对照边界

核对 OpenAI [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)、
[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) 和
[最新模型指南](https://developers.openai.com/api/docs/guides/latest-model)。
两组均用 `high`，相同常规 worker 指令、相同任务、相同 CLI 和权限。
模型选择由实际调用参数记录，不要求 worker 自证不可见的运行时字段。

本轮是 **常规 worker 小样本 pilot**，不是完整 PROVE 流程 A/B：

- 3 类脱敏合成维护任务，各模型每类 3 次，交错调用顺序；每次全新临时工作区。
- 固定初始文件、提示和外部验收的哈希；外部检查在模型退出后运行。
- 当前真实试验限 macOS；外部验收使用只读、断网沙箱和清洁环境，不把模型改写代码
  直接导入具有主线程写权限的 Python。检查实际执行的测试数，提前退出 0 不算通过。
- 先校准错误初始版本与参考实现，检查功能、范围保留及 helper 复用。
- 保留失败、超时、缺失指标；不静默重试、丢弃失败或挑最好一次。
- 记录墙钟时间和实际报告的 token。API 重定价不等于 Codex 实扣额度；没有实扣数据
  就保留 unknown，不更新 README 的节省比例。
- 不能从 3 类 Python 夹具推广到大型项目、所有语言、Astra 调度或并行吞吐。
- 既有 `scripts/benchmark_ab.py` 的完整基准门槛（至少 6 场景、3 次重复）不降低。

对照结果和角色决定见 [18 次 worker pilot](2026-09-25-worker-pilot.md)。冻结检查
全部通过，但后验共享引用检查又发现了漏测与候选错误；因此没有宣布胜者、撤掉
Terra 或更新节省比例。不能凭单位价格、单个成功案例或有限测试替换默认角色。

## 独立场景复核

使用一个新上下文、只读评估当前 Skill 与 reference，给出三个真实压力情境；
未提供预期答案。观察到容量满时排队、不抢写，权限小改不以 happy-path 直接接受，
同规则批次不按文件数量拆代理。它指出 Direct 与风险控制的关系还可更明确，已在
入口补三行说明。这里是一次包含三个情境的纸面行为探针，不是三次真实调度。

本轮运行时只增加这项澄清及 reference 中的少量调度规则，没有新角色、必填字段、
审批阶段或持久 Hook。评测脚本与数据仅留在开发目录，不随 Skill 安装。
