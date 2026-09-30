# 同类项目调研与 Sol 6.1 候选发布检查

日期：2026-09-30。结论：**可以进入发布收尾，但现在不应发布稳定版。**

本报告是修复前的审计快照；2026-10-01 的授权安装、候选 CI 和实际角色验收见[发布准备记录](../release/sol61-readiness.md)。下文缺口不作为最新状态。

Sol 6.1 主力、Astra 按问题介入、Luna 做机械批次的方向可以保留。与同类项目比较后，
未发现必须补齐另一套调度器、Hook 或固定审核团队的理由。主要缺口是可复现的安装体验问题、
关键新路径的真实证据，以及发布说明与实际配置的一致性。这个判断不是质量或节省率证明。

本轮只读研究公开一手资料，检查本地候选并运行隔离诊断；没有安装或执行第三方项目。
没有修复实现、修改全局配置、调用新的业务模型基准、提交、推送、合并或创建 Release。
仓库内只新增本报告。原有修改和 `media/` 保留。

## 1. 研究范围与版本

研究顺序：先查同类项目及 Codex 官方机制，再检查本地候选。
比较委派成本、上下文复用、写入所有权、恢复、验收证据和安装升级，不按 star 数排名。
用 deep-research 的一手证据与并行分工方法收集资料，再按 Skill Creator 的实际行为验证标准
检查候选；规则文字、确定性实现、维护者测试报告和本次实测分别记录。

下列提交由 GitHub 仓库、提交及 release API 只读核对。提交日期不表示所有文件当日更新。
读取范围中的开发分支特性不能自动当作最近正式版特性。

| 项目 | 本次固定源码 | 正式发布记录 / 许可 |
| --- | --- | --- |
| da34/codex-orchestrator | [main · df36074b74048cbca9fc987996a1e70403ec70a2](https://github.com/da34/codex-orchestrator/tree/df36074b74048cbca9fc987996a1e70403ec70a2)，09-11 | latest release API 返回 404；MIT |
| joserey7/codex-orchestrator | [main · 8f559d63a67cac4661f66b10dc1f44db5af4ae8b](https://github.com/joserey7/codex-orchestrator/tree/8f559d63a67cac4661f66b10dc1f44db5af4ae8b)，09-09 | latest release API 返回 404；MIT |
| Superpowers | [main · 8ca22dba9a94f28898bbce59f2537ff4d87c747d](https://github.com/obra/superpowers/tree/8ca22dba9a94f28898bbce59f2537ff4d87c747d)，09-25 | [v6.4.2](https://github.com/obra/superpowers/releases/tag/v6.4.2)，09-25；MIT |
| GSD Core | [next · 404482b7a36f6bc3f450948141fa28382808bd85](https://github.com/open-gsd/gsd-core/tree/404482b7a36f6bc3f450948141fa28382808bd85)，09-30 | [v1.15.0](https://github.com/open-gsd/gsd-core/releases/tag/v1.15.0)，09-26；MIT |
| oh-my-codex / OMX | [main · cdc24a71408ebd6bd0362f52170f0d7998f77007](https://github.com/Yeachan-Heo/oh-my-codex/tree/cdc24a71408ebd6bd0362f52170f0d7998f77007)，09-21 | [v0.21.6](https://github.com/Yeachan-Heo/oh-my-codex/releases/tag/v0.21.6)，09-21；MIT |
| OpenCode | [dev · 2fa3363c924c5c3e367b84a87ae478296a0ed59b](https://github.com/anomalyco/opencode/tree/2fa3363c924c5c3e367b84a87ae478296a0ed59b)，09-29 | [v1.18.33](https://github.com/anomalyco/opencode/releases/tag/v1.18.33)，09-28；MIT |
| Ponytail | [main · e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156](https://github.com/DietrichGebert/ponytail/tree/e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156)，09-14 | [v4.10.0](https://github.com/DietrichGebert/ponytail/releases/tag/v4.10.0)，09-14；MIT |

身份边界：已归档的 `gsd-build/get-shit-done` 在其
[README](https://github.com/gsd-build/get-shit-done/blob/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815/README.md)
指向 `open-gsd/gsd-core`；不要把它与 `gsd-pi` 的后继线混成一个版本。
OMX 指 `Yeachan-Heo/oh-my-codex`，不是同名或另称 v2 的仓库。

## 2. 对照结果：哪些值得吸收

### 两个轻量 Codex Orchestrator

da34 把有用的独立进展、隔离大量探索和必要独立检查作为委派理由；复杂度本身不够。
复用 worker 的有效验证，只在变更、证据不足或集成缺口时重跑。
这些主要是 [Skill 规则](https://github.com/da34/codex-orchestrator/blob/df36074b74048cbca9fc987996a1e70403ec70a2/.agents/skills/codex-orchestrator/SKILL.md)，
不是文件锁或强制验收引擎；其 [README](https://github.com/da34/codex-orchestrator/blob/df36074b74048cbca9fc987996a1e70403ec70a2/README.md)
也不保证每项任务省 token。

joserey7 区分执行难度和失败后果，并把验证、独立审核、最终接受绑定到当前 revision。
其 [Skill](https://github.com/joserey7/codex-orchestrator/blob/8f559d63a67cac4661f66b10dc1f44db5af4ae8b/plugins/codex-orchestrator/skills/orchestration/SKILL.md)
配有 [task_state.py](https://github.com/joserey7/codex-orchestrator/blob/8f559d63a67cac4661f66b10dc1f44db5af4ae8b/plugins/codex-orchestrator/scripts/task_state.py)：
后者确实检查声明状态和 revision 一致性，但明确不证明原生运行时、墙钟先后或 sandbox。

**决定：保留已有的按需委派和候选绑定证据；不引入常态预算台账、固定 review 链或模式配额。**

### Superpowers

[SDD](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/SKILL.md#L124)
将同类机械修改合批，限制 reviewer 再委派，保存恢复材料，并限定修复轮数；这些首先是提示词约定。
[review-package](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/scripts/review-package#L20)
有实际的祖先关系与非空 commit 范围检查，但不会自动把脏工作区算进审核。
[完成前验证规则](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/verification-before-completion/SKILL.md)
要求真实输出与退出码，不接受 agent 自报成功。

**决定：保留同批合并、原 worker 修复、有限恢复和真实 diff 检查；不复制全套规划/TDD/逐任务审核流程。**
上游 release 的耗时、token 和缺陷探针结果是维护者报告，不迁移为 PROVE 收益。

### GSD Core

当前 `next` 的 [隔离契约](https://github.com/open-gsd/gsd-core/blob/404482b7a36f6bc3f450948141fa28382808bd85/gsd-core/references/dispatch-isolation-gate.md)
区分 harness worktree、orchestrator worktree 和无隔离；
[quick-batch 决策代码](https://github.com/open-gsd/gsd-core/blob/404482b7a36f6bc3f450948141fa28382808bd85/src/quick-batch-dispatch.cts#L98)
在无隔离且写入时限制并发。实际派发仍依赖工作流执行该决定。

[指纹检查](https://github.com/open-gsd/gsd-core/blob/404482b7a36f6bc3f450948141fa28382808bd85/src/verification.cts#L1491)
能识别覆盖材料变化导致的 stale，但不能证明测试执行过或覆盖文件集合完整。
[path guard](https://github.com/open-gsd/gsd-core/blob/404482b7a36f6bc3f450948141fa28382808bd85/hooks/gsd-worktree-path-guard.js#L144)
仅覆盖部分工具/路径情形，不是通用 sandbox。

**决定：借鉴能力未知与明确可用的区分、证据失效范围、失败现场由单一 owner 保留。**
PROVE 已有对应规则；优先补实际故障测试，不为这些概念另造 Hook 总线或阶段管理系统。

### OMX

[任务状态实现](https://github.com/Yeachan-Heo/oh-my-codex/blob/cdc24a71408ebd6bd0362f52170f0d7998f77007/src/team/state/tasks.ts#L71)
确实有锁、版本比较、claim token、租期及状态转移检查。它保证任务声明的所有权，不等于文件写入锁。
[运行时契约](https://github.com/Yeachan-Heo/oh-my-codex/blob/cdc24a71408ebd6bd0362f52170f0d7998f77007/docs/contracts/team-runtime-state-contract.md#L19)
将任务完成、集成及最终交付区分开，值得保留。

但 [verification presence 检查](https://github.com/Yeachan-Heo/oh-my-codex/blob/cdc24a71408ebd6bd0362f52170f0d7998f77007/src/verification/verifier.ts#L23)
只识别类似验证记录的文本，包含 FAIL 也可能满足 presence；不能当作测试通过证据。
当前 [默认模型配置](https://github.com/Yeachan-Heo/oh-my-codex/blob/cdc24a71408ebd6bd0362f52170f0d7998f77007/src/config/models.ts#L113)
各档均为 Astra，也不能为低成本路由背书。

**决定：保留 assigned/completed/integrated/accepted 的区分；不引入完整常驻运行时或关键词自动扩散。**
没有实际并发状态丢失证据前，持久租约不是本版必需品。

### OpenCode

[task 实现](https://github.com/anomalyco/opencode/blob/2fa3363c924c5c3e367b84a87ae478296a0ed59b/packages/opencode/src/tool/task.ts#L104)
有模型继承、按 task ID 恢复及实际嵌套深度检查。
[权限继承实现](https://github.com/anomalyco/opencode/blob/2fa3363c924c5c3e367b84a87ae478296a0ed59b/packages/opencode/src/agent/subagent-permissions.ts)
与 [回归测试](https://github.com/anomalyco/opencode/blob/2fa3363c924c5c3e367b84a87ae478296a0ed59b/packages/opencode/test/agent/plan-mode-subagent-bypass.test.ts#L29)
表明父 agent 配置限制与父 session deny 规则不是同一回事，子 agent 有自己的权限配置。

其 [内置 agent](https://github.com/anomalyco/opencode/blob/2fa3363c924c5c3e367b84a87ae478296a0ed59b/packages/opencode/src/agent/agent.ts#L156)
即使禁用 edit 仍可能有 bash；不能把角色叫作 read-only 就等同 OS 只读。
这些是 OpenCode 的机制，不能直接套用为 Codex 的权限行为。

**决定：新增证据应检验角色加载、权限边界和恢复行为；不只验证配置中存在某个字段。**
不复制另一宿主的 agent schema，也不把会话恢复当作业务验收。

### Ponytail

[Skill](https://github.com/DietrichGebert/ponytail/blob/e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156/skills/ponytail/SKILL.md)
强调先理解受影响流程、复用已有能力、保留安全与明确需求。
[agentic benchmark](https://github.com/DietrichGebert/ponytail/blob/e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156/benchmarks/agentic/README.md)
用真实 agent 的文件结果而非回答长度比较，区分完整性、安全性和代码体积，并校准好/坏参考实现。
其具体执行隔离与 judge 仍需另审；本次没有运行该 harness。

**决定：继续保留已适配的最小实现原则和完整性门槛；拒绝只用 LOC、单价或上游成绩证明收益。**

### Codex 官方边界

[子代理文档](https://learn.chatgpt.com/docs/agent-configuration/subagents) 当前明确：
子代理本身增加 token 消耗；自定义角色文件中的模型/effort 有自己的优先级；角色文件须被宿主实际加载。
CLI 的父会话实时权限覆盖也可重新应用到子代理，所以 TOML 意图不自动等于最终强制边界。

09-11 的 [Astra 提示与 Skill 指南](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
建议短描述、渐进加载及删除无用流程，并提醒不同模型需要的指导不同。
**推断：** 这支持保留当前轻量入口，但不证明 Sol 6.1/high 是所有任务的最佳配置。

本报告只借鉴思想与检查方法，没有复制上述项目的实质实现；既有 Ponytail MIT 归属保留不变。

## 3. 本地证据：现在到底通过了什么

实际工作树为 `codex/sol61-lean-routing`，HEAD 为
`a30e84c581a357b6cd5f1f6eb9f2c4a3f73c19d4`，候选仍有未提交改动。
本轮没有把 HEAD 或旧版徽章称为当前候选 CI。

| 检查 | 本轮结果 | 边界 |
| --- | --- | --- |
| 源码身份 | 报告写入前，原目录与隔离副本的 95 个 Git 列出文件 SHA-256 全部一致 | 包含自有 tracked/untracked 候选文件；排除无关 `media/`，不是完整工作目录相同 |
| 自动测试 | 隔离副本重新运行 `bash scripts/test.sh`：122 tests，30.665 s，OK，exit 0 | 配置/文本契约加真实隔离安装、卸载、恢复等；不是 122 次模型实跑 |
| 隔离源码校验 | `bash scripts/validate.sh`：PASS，exit 0 | 本机没有 pwsh；PowerShell 是结构检查，不是原生执行 |
| 原目录校验 | 同一命令：FAIL，exit 1 | 扫入 `media/x-promo/node_modules/memfs/README.md` 的不存在链接，见 R1 |
| 自定义模型诊断 | 默认配置 `install.sh --check` 为 0；仅在一次性副本改 worker 模型后为 1 | 没有真实安装，测试目标目录始终不存在；见 R2 |
| 已有真实联跑记录 | [Sol 6.1 Compatibility smoke](../../tests/artifacts/sol61-live-smoke.md) 及 JSON 回执已回读 | 一条预选 Compatibility 路由；12 项 fixture 检查与补充探针，不是完整发布验收 |
| Windows / Linux 候选 CI | 本轮未运行 | 现有 workflow 文件和旧版成功记录不等于本候选通过 |

已有的静态候选测试正确地将旧 v1.1.0 回执与新角色映射分开；
POSIX 也已有旧四角色配置升级、故障回滚和恢复原模型/权限的测试。
本轮未发现这些已测试路径的新失败，不表示其他路径无缺陷。

## 4. 发布前必须收尾的事项

### R1 — 发布校验范围被素材依赖污染

已复现：原目录运行 `bash scripts/validate.sh` 返回 1。
只在内存里给验证器增加路径诊断，定位到 `memfs/README.md` 引用了未附带的 `docs/api-status.md`。
根因是 [validate.sh](../../scripts/validate.sh) 第 223–246 行递归检查整个根目录的 Markdown，
第 256 行后的文本扫描也未排除依赖树。失败输出只给一条合并错误，不能直接定位文件。

这是已有扫描边界问题被当前素材目录触发，不是 Sol 6.1 模型错误。
`media/` 尚未跟踪，不能推断干净发布包一定失败；隔离源码确实通过。

最小处理：明确发布文件集并对最终干净候选验证；如果保留素材开发目录，限定自有源码扫描范围，
保留对全部待发布文件的链接/敏感内容检查，并给出不泄密的具体路径与错误种类。
不删除用户素材，不用停掉校验掩盖失败。验收应同时覆盖干净 checkout 和存在被忽略依赖的开发目录。

### R2 — README 的“改模型后重装”实际不可用

[中文](../../README.md) 与 [英文](../../README.en.md) 第 127–129 行允许更换 profile 的模型/effort，
然后 validate、reinstall。但 [POSIX validator](../../scripts/validate.sh) 第 184–210 行
及 [PowerShell validator](../../scripts/validate.ps1) 第 150–160 行要求精确等于内置默认值；
两个安装器都先调用该校验。

隔离复现：默认源码的 `install.sh --check` 通过；仅把
`prove-complex-worker.toml` 中 `gpt-6.1-sol` 改为宿主可用的 `gpt-6-sol`、其他内容不变，
再运行即报 `source validation failed`，exit 1。此诊断没有调用模型，也没有写入测试安装目标。
HEAD 中也存在精确值比较，因此这是继承的可用性/说明冲突，不是本轮新引入。

最小处理二选一：明确本版只支持预置 profile；或区分“仓库默认值回归检查”和
“可安装自定义配置的合法性检查”。不能只让用户修改模型再重复运行必然拒绝的安装命令。
不需要为此新增复杂模型注册表。

### R3 — 核心新行为的证据仍未覆盖

[现有回执](../../tests/artifacts/sol61-live-smoke.md) 如实记录了预设的 plan-first Compatibility；
其 controller、executor、reviewer 都是显式选择的 generic Sol 6.1 上下文。
Host + Sol 并行不等于两个 Sol worker 并行；该次成功也不证明默认 Solo 没有多派规划者。

建议发布前补三组有边界的实际检查，可共用临时 fixture，不追求大而全：

1. **默认路由和加载：** 新会话发现 Skill/四个角色映射；自然任务触发 Direct、连贯多文件 Solo、
   Assist 只分析。记录真实派发数量与模型/effort，避免 harness 预先指定答案。
2. **改变的分工：** 两个独立 Sol 写域、单独 Luna 机械批次、Astra 专项只读咨询及返回原 owner 修复。
   记录文件边界、依赖、真实检查；在可强制权限的宿主额外做负向写入检查。
3. **恢复：** 至少一次“超时但写进程仍存活”和一次同文件冲突，确认不启动竞争写者，
   保留已有 diff、停止已识别任务进程后才转交；恢复后重跑受影响检查。

这些是本次审计提出的收尾建议，不是已经执行的测试。
新会话/全局安装需要后续明确安排；本轮没有改全局或把旧会话映射当作候选生效。

### R4 — 当前候选的跨平台升级与 CI 还没有闭环

已有 macOS 隔离套件通过，不必推倒重测设计。
但 [Windows lifecycle](../../tests/windows-lifecycle.ps1) 当前专门构造的是 v1.0 三角色升级，
没有与 POSIX 新增用例对应的“v1.1.0 四角色原模型/权限 → 新映射 → 恢复”的专门夹具；
而 Python 的 POSIX lifecycle 在 Windows 上会跳过。

最小处理：补 Windows 四角色重映射/恢复回归，然后让最终发布 SHA 跑现有
[POSIX](../../.github/workflows/posix-validation.yml) 与
[Windows](../../.github/workflows/windows-validation.yml) 矩阵。
现有矩阵覆盖 Linux/macOS、Python 3.11/3.13、Windows 两个 runner 与 PowerShell 5.1/7。
本轮不为获取 CI 而自行推送或触发外部发布。

### R5 — 发布材料仍描述旧版，权限表述也应更精确

两份 README 明确提醒正文/配图仍是 v1.1.0，这是开发期诚实标注，不能带着它直接宣告新版完成。
发布前同步正文、两套 SVG、模型要求、Terra FAQ、安装升级说明、成本页、发布记录和运行时矩阵。
旧 62.3% 是预算例子，不能成为新方案的收益；历史回执应保留，不改写为新版证据。

[runtime-notes](../../.agents/skills/codex-prove/references/runtime-notes.md) 第 64 行的
“have read-only sandboxes”建议改为“profiles request read-only”，并说明实际权限由宿主决定。
后文已有 Desktop 限制说明及危险操作 fail-closed 规则，问题是前一句过于绝对；
官方 CLI 的父会话覆盖同样需要考虑，不只 Desktop。

## 5. 这一版不必增加什么

- 不必复制 OMX/GSD 的常驻状态库、租约、Hook 总线或阶段管理。它们解决更重的运行时需求。
- 不必要求每项任务独立审核，也不必固定使用全部角色；当前按风险和独立进展决定的方式合理。
- 未验证的 Native Nested、物理 Windows Desktop 可以继续标为 UNVERIFIED，不阻塞只承诺已验证路径的版本。
- 没有“更省/更快”的量化承诺时，完整成本 A/B 不必成为唯一发布门槛；若要宣传收益，就必须先跑
  同任务、同起点、同预算、交错重复、包含全部开销和失败的真实对照。不能用单价替代结果。
- 不以缺少 CounterProof 适配器或第二个审批层作为缺口。候选证据是否充分仍由 PROVE 自己判断。

## 6. 建议的有限发布顺序

1. 先处理 R1/R2 的安装与说明冲突，补 R4 的 Windows 升级夹具，形成明确的发布文件集。
2. 完成 R3 三组实际检查，保存精确配置、candidate、输出、退出码和未验证项。
3. 同步 R5 文档与素材，运行最终候选校验及跨平台 CI；检查实际 diff、许可与文件范围。
4. 用户确认后再执行需要授权的安装/发布动作；以最终 SHA 绑定新发布记录，不复用旧版成功徽章充数。

验收完成即可发布，不额外开启新架构工程。
