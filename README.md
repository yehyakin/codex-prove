[简体中文](README.md) · [English](README.en.md)

> **v1.2.0 · Sol 6.1 主力分工。** 本页描述此版本源码；正式发布状态、标签与 CI 以 [GitHub Release](https://github.com/yehyakin/codex-prove/releases/tag/v1.2.0) 为准。详见[版本说明](docs/release/v1.2.0.md)；[历史准备记录](docs/release/sol61-readiness.md)保留较早候选的验收范围。

配图保留制作时的候选标记与日期，不表示当前发布状态。

<p align="center">
  <a href="https://github.com/yehyakin/codex-prove/releases"><img alt="Release" src="https://img.shields.io/github/v/release/yehyakin/codex-prove?style=flat-square"></a>
  <a href="https://github.com/yehyakin/codex-prove/actions/workflows/posix-validation.yml"><img alt="Linux / macOS CI" src="https://img.shields.io/github/actions/workflow/status/yehyakin/codex-prove/posix-validation.yml?branch=main&amp;label=Linux%20%2F%20macOS&amp;style=flat-square"></a>
  <a href="https://github.com/yehyakin/codex-prove/actions/workflows/windows-validation.yml"><img alt="Windows CI" src="https://img.shields.io/github/actions/workflow/status/yehyakin/codex-prove/windows-validation.yml?branch=main&amp;label=Windows&amp;style=flat-square"></a>
  <a href="LICENSE"><img alt="Apache-2.0 License" src="https://img.shields.io/github/license/yehyakin/codex-prove?style=flat-square"></a>
</p>

# Codex PROVE

**让 Sol 把活做完，需要帮手时再分工。**

PROVE 是给 Codex 用的模型分工 Skill。**Sol 6.1 做主力，Astra 解难题，Luna 做批量。** 一条完整任务尽量留在一个上下文里，只有能独立推进的工作才拆开。

改个文案、修个小问题，当前 Codex 直接做。一个功能即使涉及几个文件，也不必先开规划代理、再开执行代理。你说清目标和边界，PROVE 决定是否需要帮手，并检查实际结果。

[成本预算](#成本预算) · [怎么分工](#怎么分工) · [安装](#安装) · [怎么用](#怎么用) · [交付前检查](#交付前检查)

## 成本预算

**一组预算示例：相对全 Astra，375 → 64.5 credits，少 82.8%。** 这是按公开费率和假设工作量计算的预算，不是实测节省。

![预算示例：全 Astra 为 375 credits，Sol 80% 与 Luna 20% 分工加额外开销为 64.5 credits，少 82.8%；非实测](docs/assets/readme/livecanvas/cost-budget/cost-budget-zh.png)

按 **2026-10-01 Codex Standard** 费率，假设累计 **1M 非缓存输入 + 0.1M 输出（含计费推理）**，输入和输出各按 **Sol 80% / Luna 20%** 分配。模型费用为 60.75 credits，另加 3.75 credits 的协调预算，合计 64.5。这里的额外开销是**全 Sol 费用的 5%**，不是全 Astra 的 5%；80/20 也不是任务的固定配额。

这个例子不含额外 Astra 咨询、工具费、人工成本或等待时间，不保证不同模型有同等质量，也不代表订阅月费或每周额度的变化。真实任务的缓存、上下文、审核和返工会改变结果。计算过程、费率来源和历史算例见[成本说明](docs/costs.md#sol-61-预算示例--2026-10-01)；也可[查看动态图](docs/assets/readme/livecanvas/cost-budget/cost-budget-zh.gif)。

## 怎么分工

先选最简单的可行方式，不要求每次用齐所有模型。

![Sol 6.1 负责完整任务，Astra 只读解难题，Luna 处理规则明确的机械批量；不要求每次用齐所有模型](docs/assets/readme/livecanvas/polish/routing-zh.png)

| 模型 | 负责什么 | 默认推理等级 |
| --- | --- | --- |
| GPT-6.1 Sol | 完整任务、常规开发、必要的协调和验收 | high |
| GPT-6 Astra | 一个明确难题，或独立风险评审；只读 | high |
| GPT-6 Luna | 规则明确、结果可检查的机械批量任务 | max |

如果当前 Codex 已是 Sol 6.1，就复用当前会话及其已确认的推理等级。独立批量可以直接交给 Luna，不必先开 Sol 做计划。Astra 不是每次都要走的审批环节。

| 任务 | 怎么做 |
| --- | --- |
| 小修改、明确问答（Direct） | 当前 Codex 直接完成，零子代理 |
| 一条完整功能或排查（Solo） | Sol 自己规划、实现和检查，不另开规划代理 |
| 只分析、只评审（Assist） | Sol 分析；具体难题或独立风险评审按需找 Astra，不改代码 |
| 多条独立工作线（Coordinated） | Sol 协调并行，明确各自改哪些文件 |

少传上下文、少开空代理，是这个版本的设计目标，不是已测得的节省比例。已有[单任务三组 A/B 对照](docs/research/2026-10-02-three-arm-results.md)：三组均通过 19/19 独立检查，也都没有委派子代理。PROVE 本例比普通 Codex 的 API 等价估算低 13.86%、用时短 10.20%，但比定制 Host 的 da34 组估算高 0.61%、用时长 9.36%。**每组仅一次，不证明普遍节省或混合模型分工优势。** 上面的预算示例不是本次实测值。[查看分工动态图](docs/assets/readme/livecanvas/polish/routing-zh.gif)

## 安装

需要 Git、Python 3.11+，以及支持自定义 Agent 的 Codex。默认配置使用上面三个模型；一次任务只需它实际用到的模型可用。安装前确认账号支持对应模型和推理等级。

以下命令拉取 `main`。如需固定 v1.2.0，请先确认 [Release](https://github.com/yehyakin/codex-prove/releases/tag/v1.2.0) 已发布，再在克隆目录执行 `git checkout v1.2.0` 后验证、安装。安装需要完整 Git 工作区，不支持直接使用无 Git 元数据的源码压缩包。旧 [v1.1.0](https://github.com/yehyakin/codex-prove/releases/tag/v1.1.0) 的分工和运行记录不作为本版验收。

### macOS / Linux

```sh
git clone https://github.com/yehyakin/codex-prove.git
cd codex-prove
bash scripts/validate.sh
bash scripts/install.sh
```

### Windows

Windows PowerShell 5.1：

```powershell
git clone https://github.com/yehyakin/codex-prove.git
Set-Location codex-prove
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
```

如果用 PowerShell 7，在仓库目录里运行：

```powershell
pwsh -NoProfile -File scripts/validate.ps1
pwsh -NoProfile -File scripts/install.ps1
```

安装器会先备份旧版，不改你原有的 `~/.codex/config.toml`，也不动其他 Agent。装好后开一个新的 Codex 会话。

## 怎么用

在任务前加上 `$codex-prove`，然后正常说你要做什么：

```text
$codex-prove 给项目加一个账号设置页，能改昵称和头像。
沿用现有登录接口和 UI，别动支付模块，做好后跑一下测试。
```

不用填表，也不用指定开几个子代理。把目标和不能动的地方说清楚就行。

比如上面的账号设置页，通常由一个 Sol 看接口、改页面、跑测试。只有确实能独立推进的模块才拆开；遇到一个难以确定的问题，再请 Astra 专项分析；有足够多的重复修改才交给 Luna。

如果只想讨论方案，也可以直接说：

```text
$codex-prove 看看这个项目的登录方案，比较一下怎么改更合适，先别改代码。
```

**只有你写了 `$codex-prove` 才会启用。** 平时照常用 Codex；即使叫了 PROVE，简单任务也会直接完成，不额外开子代理。默认用简体中文回复，想换语言直接说。

## 交付前检查

**“代理说完成了”不等于交付完成。** PROVE 要检查真实文件、执行验证并核对需求覆盖；未通过的项目继续处理，需要新权限或关键选择时才交给你决定。验收看证据，不要求 Astra 每次签字。

![交付前核对真实文件、验证输出与需求覆盖，再决定是否通过；不能只采信代理的完成声明](docs/assets/readme/livecanvas/polish/evidence-zh.png)

[查看验收动态图](docs/assets/readme/livecanvas/polish/evidence-zh.gif)

<details>
<summary>并行修改时，怎样避免写入冲突？</summary>

每个写入范围只安排一个活跃负责人。交接前先停止原代理及其写入进程，检查并保留改动，再交给新负责人继续。不能一边让旧代理写，一边让新代理接手同一范围。

![一个写入范围只有一个活跃负责人；交接顺序是停止旧写入、检查并保留改动、再启用新负责人](docs/assets/readme/livecanvas/polish/ownership-zh.png)

这些是工作流约束，不是文件锁或隔离机制；它们不能阻止外部编辑器或其他进程写入。[查看交接动态图](docs/assets/readme/livecanvas/polish/ownership-zh.gif) · [完整调度说明](.agents/skills/codex-prove/references/orchestration.md)

</details>

## 这次更新了什么

这次主要减少上下文往返和不必要的角色接力。

- **Sol 优先。** Sol 6.1 接替常规执行和协调，Terra 退出默认分工；保留四个稳定角色 ID，不要求四个角色全上。
- **完整任务不拆碎。** Solo 自己规划、实现和检查，只有独立工作才并行。
- **Astra 按问题调用。** 用于难题或有必要的独立评审，不做例行签字。
- **少跑空流程。** 能从调用记录确认模型，就直接开工，不再先让子代理回答一轮“我是谁”。
- **能继续的就继续。** 已经授权的本地修改和测试，不会因为一次失败或少了一个标题就停下来找你批准。需要新权限或关键选择时才问你。
- **少写没必要的代码。** 借鉴 Ponytail，先看项目里有没有、标准库能不能做，再考虑新依赖和新抽象。

本版变更和证据边界见[版本说明](docs/release/v1.2.0.md)、[发布准备检查表](docs/release/sol61-release-checklist.md)和[最新同类项目调研](docs/research/2026-10-02-competitive-orchestration.md)。[历史准备记录](docs/release/sol61-readiness.md)、[v1.1.0 发布记录](docs/release/v1.1.0.md)与[历史兼容性记录](docs/release/runtime-surface-matrix.md)保留原有范围，不自动覆盖新版。

## 几个常见问题

**子代理越多越快吗？**

不一定。独立任务可以并行，但拆任务、传上下文、等结果也要花时间。PROVE 只开有必要的子代理，数量还受当前 Codex 的线程上限影响。

**Terra 去哪里了？**

Terra 不再是默认执行模型。`prove-complex-worker` 这个角色 ID 保留，模型改为 Sol 6.1。名称不绑模型，后续升级不用改入口。用户明确指定的模型不会被悄悄替换。

**我能改模型吗？**

可以，配置在 [`.codex/agents/`](.codex/agents/prove-controller.toml)。Sol、Astra 默认 `high`，Luna 用 `max`。校验器检查 TOML、模型标识和推理等级格式，不把模型锁死为默认值，也不能证明账号有调用权限。确认可用后重新检查、安装，并开新会话核对实际角色映射。详细设置见[模型配置说明](.agents/skills/codex-prove/references/runtime-notes.md)。

**以前的 Sol Control 还能用吗？**

可以，`$sol-control` 仍保留为兼容入口。项目现在叫 Codex PROVE，以后换模型不需要再改名字。[更名说明](CODEX_PROVE_V1_IMPLEMENTATION_REPORT.md)

**装好了却找不到 Skill，或者模型调用失败？**

先开新会话，确认安装成功、对应模型在你的 Codex 里可用。只拉取源码不会更新全局安装；旧会话也不会自动换配置。仍有问题可以发 [Issue](https://github.com/yehyakin/codex-prove/issues/new/choose)，附上系统版本、Codex 版本和去掉敏感信息的报错。

## 更新和卸载

更新前先运行 `git status --short`，有自己的改动就先保留。工作区干净后：

```sh
git switch main
git pull --ff-only origin main
```

然后重跑上面对应系统的检查和安装命令，打开新会话。安装器会输出备份路径；遇到本地文件被手动修改的情况会停下来，不会直接覆盖。

<details>
<summary>卸载，或恢复上一次备份</summary>

macOS / Linux：

```sh
bash scripts/uninstall.sh
# 如果要恢复上一次备份，改用：
bash scripts/uninstall.sh --restore-latest
```

Windows PowerShell 5.1：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1
# 恢复上一次备份：
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1 -RestoreLatest
```

PowerShell 7：

```powershell
pwsh -NoProfile -File scripts/uninstall.ps1
# 恢复上一次备份：
pwsh -NoProfile -File scripts/uninstall.ps1 -RestoreLatest
```

只卸载本项目安装的文件，不删除其他 Skill 或 Agent。

</details>

## 反馈和参与

维护者：[@yehyakin](https://github.com/yehyakin)。支持 macOS、Linux 和 Windows，维护当前 `main` 和最新发布版，具体见 [SUPPORT.md](SUPPORT.md)。这是社区项目，不是 OpenAI 官方产品。

欢迎提 Issue、发 PR，也欢迎直接说哪里不好用。贡献前看一下 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。想了解内部怎么分工，可以读 [Skill](.agents/skills/codex-prove/SKILL.md) 和[调度说明](.agents/skills/codex-prove/references/orchestration.md)。

安全问题请按 [SECURITY.md](SECURITY.md) 通过[私密漏洞报告](https://github.com/yehyakin/codex-prove/security/advisories/new)联系，不要把 Token、私有配置或项目代码贴进公开 Issue。

## 参考与许可

这个项目参考了 [Ponytail](https://github.com/DietrichGebert/ponytail) 的精简思路、[Superpowers](https://github.com/obra/superpowers) 的任务拆分与审核，以及其他社区编排项目。[调研记录](docs/research/2026-09-25-peer-orchestration.md)和 [NOTICE](NOTICE) 保留了具体来源与归属。

采用 [Apache License 2.0](LICENSE)。

**致谢 / Thanks**

感谢 [LINUX DO 论坛](https://linux.do/) 社区的关注、反馈与支持
