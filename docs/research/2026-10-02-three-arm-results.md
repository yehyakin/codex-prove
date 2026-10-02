# Sol 6.1 候选版：单任务三组对照

日期：2026-10-02（Asia/Shanghai）。这是一次有限案例记录，不是通用性能榜单，也不是发布完成公告。

## 结果

三组最终都通过同一套独立验收 **19/19**，原始实现为 **9/19**。PROVE 本例相对普通 Codex 的 Standard API 等价估算低 **13.86%**、运行时间短 **10.20%**；相对定制 Host 的 da34 组，估算高 **0.61%**、时间长 **9.36%**。每组只有一次，不能据此判定稳定优势。

| 组别 | 独立验收 | CLI 运行时间 | Standard API 等价估算 |
| --- | ---: | ---: | ---: |
| da34/codex-orchestrator，定制共同 Host | 19/19 | 230.664 秒 | $0.1739244 |
| 普通 Codex，无上述编排 Skill | 19/19 | 280.917 秒 | $0.2031256 |
| PROVE 冻结候选，实际 Direct | 19/19 | 252.253 秒 | $0.1749800 |

三组均未委派子代理。因此，这次验证的是一个小任务的直接执行结果，**不证明 Sol/Luna 混合分工收益、复杂任务路由能力或并行提速**。也没有依据声称 PROVE 胜过选定竞品。README 的 82.8% 仍只是另一组预算假设，不是本次实测值。

## 固定输入和差异

- 一个已有项目中的多语言记录搜索任务：空白分词后全部命中、查询与数据双向 NFKC、只检索允许的语言字符串、忽略元数据/非字符串、保留单字段别名短语边界，并且不修改输入。
- 三组从同一份 **749 文件**快照和依赖快照开始。只允许改实现及测试两个文件；最终逐文件核对确认净差异恰为这两个文件，原有测试保留，注入的 Skill/角色文件未变。检查不覆盖依赖缓存、系统临时文件或所有中途写入。
- 同一 Codex CLI **0.159.2**；启动选定并在 `turn_context` 观察到 `gpt-6.1-sol/high`。共同设置 `workspace-write`、`approval_policy=never`、沙箱网络关闭、最多 3 个子代理、1200 秒限时。没有超时或续跑。沙箱网络限制不表示 CLI 自身不联网。
- PROVE 使用 11 文件冻结运行包，SHA-256：`72d3f417ea4559bf1a5afa71448c79c6f5570b3f43a4ca1e3458909d60c674e0`。本轮评分和发布文档不改变它。
- da34 固定 [MIT 许可源码提交 `df36074…`](https://github.com/da34/codex-orchestrator/tree/df36074b74048cbca9fc987996a1e70403ec70a2)。将 Host 从 Astra/medium 改为共同 Sol 6.1/high，并发上限从 4 改为 3；原生子角色配置保持不变。**这不是上游原厂 Pro 默认配置的产品对比。** 未把上游代码或私有项目源码打包进 PROVE。
- 固定顺序为 da34 → 普通 Codex → PROVE，无随机顺序、无重复试验。共用安装环境和可见的环境技能/插件，非完全隔离；顺序、缓存和后台负载均可能影响结果。工作区是文件快照而非 Git checkout。

## 独立质量验收与失败历史

验收沿用运行前定义的 19 项确定性检查，评分器未提供给参测代理。复验原始实现仍为 9/19，三组最终产物均为 19/19；没有为了接受答案而更换评分标准。另行重跑各组最终自写单测，分别为 52/52、64/64、46/46，三组 TypeScript 检查均退出 0。不同的自写用例数量不是质量排名；本次没有做应用构建、浏览器或生产发布验收。

成功不等于全程无错误。保存的原始记录包含：

- da34 和普通 Codex 各一次无 Git 元数据导致的退出 128，以及一次预期的红灯测试退出 1；另各有一条工具包装层失败遥测。
- PROVE 一次红灯测试退出 1，随后两次类型检查退出 2，修正测试夹具的类型断言后才通过；另有一条路径未明的文件系统沙箱拒绝警告。
- 三组 stderr 均有环境 MCP 授权和生命周期警告，不能将其说成“stderr 为空”。三组 CLI 最终均退出 0，未报告 `error` / `turn.failed` 事件。

这些尝试都在原始 CLI 时间窗和累计用量里，没有删掉失败成本。最终净差异检查和验收通过不用于抹去警告，也不扩大为系统级无副作用证明。

## 用量、费用和覆盖范围

| 组别 | 输入（含缓存） | 缓存输入 | 输出（含推理） | 唯一响应数 |
| --- | ---: | ---: | ---: | ---: |
| da34 | 278,851 | 235,904 | 6,444 | 8 |
| 普通 Codex | 347,363 | 300,416 | 7,919 | 10 |
| PROVE | 336,976 | 298,880 | 6,890 | 10 |

按 `(thread_id, turn_id, response_id)` 去重后，逐响应之和与最后的 turn/thread 累计、token 事件累计及 CLI 完成事件的对应字段一致。累计快照不相加，缓存是输入子集，推理是输出子集。三组均记录 0 cache-write tokens，最大单请求输入分别为 49,021、52,513、49,570。

同时检查运行日期的本地活跃/归档 session 元数据，递归查找父子关系，并核对 CLI/rollout 委派调用：本次三组均未发现子会话或委派。因而可核对这三个 **CLI 调用内的全部已报告用量**，而非把通用 root-only 探针当成全树计量器。提供方未报告的重试/费用仍未知。

估算统一使用 2026-10-02 核对的 [OpenAI API Standard 费率](https://developers.openai.com/api/docs/pricing)：每百万非缓存输入 $2、缓存输入 $0.10、输出 $10。单请求输入均低于 [Sol 6.1 的 272K 长上下文门槛](https://developers.openai.com/api/docs/models/gpt-6.1-sol)，不按整场累计输入触发长上下文价。

```text
API equivalent = ((input - cached) × 2 + cached × 0.10 + output × 10) / 1,000,000
```

启动请求 `service_tier=default`，但实际服务层级没有提供方回执；以上是统一费率换算，**不是实际账单、Codex credits、订阅额度或现金节省**。计时从 runner 启动该 CLI 到退出，包含它的工具执行与修复；不含依赖准备、外层协调和事后独立评分的人机成本，不能称为完整发布工程的端到端成本。

## 公开材料和结论边界

[脱敏数值回执](2026-10-02-three-arm-results.json)包含原始记录哈希、逐响应用量、评分结果、时间、费用公式及未知项。私有项目、原始提示词、会话正文、账号日志和机器路径不公开；因此这是可复算数字的案例，不是第三方可直接重跑的公开 benchmark。

这次关闭了“当前冻结候选尚无同任务质量/用量/时间记录”的缺口。仍没有重复性统计、混合模型收益、复杂任务路由或普遍胜过竞品的证据。发布定位应保持轻量、显式启用、按需分工；无需为了制造优势强制开子代理。其余放行条件见[发布检查表](../release/sol61-release-checklist.md)。

## English summary

One task, one trial per arm, fixed order, shared ambient environment. All three passed the same independent 19-case oracle; the original implementation passed 9. PROVE used Direct with no descendants: 252.253 seconds and a normalized Standard API equivalent of $0.1749800, versus ordinary Codex at 280.917 seconds / $0.2031256 and the host-customized da34 configuration at 230.664 seconds / $0.1739244. This is 13.86% lower estimated cost and 10.20% less time than the baseline, but 0.61% higher estimated cost and 9.36% more time than da34. It is not a repeatability, mixed-model routing, subscription-savings, or product-superiority claim. Raw private project data is withheld; the numerical receipt is not a publicly runnable benchmark. Provider tier and actual billing remain unknown; preparation and post-run grading are excluded.
