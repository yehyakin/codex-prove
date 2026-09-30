# 成本说明 / Cost notes

[返回中文 README](../README.md) · [Back to the English README](../README.en.md) · [English explanation](#english)

这里保留历史预算和计算方法。价格带日期保留，避免把不同版本的数字混在一起。

## Sol 6.1 候选版 / Candidate

当前默认分工是 Sol 6.1 主力、Astra 只读咨询、Luna 机械批量。减少上下文传递和不必要的代理是设计目标，**尚无同任务成本、速度或质量 A/B 结论**。实跑验证不能替代对照实验。

新版不沿用旧版的 token 分配比例，也不宣称节省 62.3%。未来比较应固定任务、起点和验收条件，记录实际模型、输入/缓存/输出、重试、协调、耗时和通过率，再使用执行当日适用费率计算。单次 smoke 或模型单价不能证明整体收益。

Sol 6.1 is the main model, Astra a read-only adviser, and Luna a mechanical batch worker. There is **no same-task cost, speed, or quality A/B result** for this candidate. Historical savings below are not candidate results. See the [candidate design](research/2026-09-30-sol61-routing.md) and [release evidence](release/sol61-readiness.md).

## v1.1.0 历史费率 / Historical rates · 2026-09-26

以下均为 Standard、每 1M tokens 的费率；短上下文指单次请求输入不超过 272K。累计 1M 输入可以分布在多次请求中。

| 模型 / Model | API 输入 / Input | API 缓存 / Cached | API 输出 / Output | Credits 输入 / Input | Credits 缓存 / Cached | Credits 输出 / Output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6 Astra | $10.00 | $1.00 | $50.00 | 250 | 25 | 1,250 |
| GPT-6 Sol | $2.00 | $0.20 | $10.00 | 50 | 5 | 250 |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 | 50 | 5 | 300 |
| GPT-6 Luna | $0.10 | $0.01 | $0.50 | 2.5 | 0.25 | 12.5 |

来源 / Sources：[OpenAI API pricing](https://developers.openai.com/api/docs/pricing)、[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)、[Codex credits](https://learn.chatgpt.com/docs/pricing)。账单以使用时适用的价格为准 / Check the rates that apply when you run the task.

相对 Astra，Sol 的输入和输出都是 20%；Terra 分别为 20% 和 24%；Luna 都是 1%。这里比较的是同类 token 的单价，不是整个任务的费用。Sol 与 Terra 输入同价，Sol 输出更低价，保留 Terra 不能只用“便宜”解释。

## v1.1.0 README 的历史预算例子

假设：

- 累计 1M 非缓存输入 + 0.1M 输出，每次请求都在上面的短上下文范围内。
- 每类 token 按 Astra 20% / Sol 20% / Terra 40% / Luna 20% 分配。
- 另加全 Astra 基线费用的 5%，作为额外规划、传递上下文和审核开销。
- 不含工具附加费、人工成本、等待时间；不假定不同模型一定给出同样质量的结果。

按上面的 token 量，全程使用每个模型分别是 $15.00、$3.00、$3.20、$0.15。因此：

```text
baseline = 1M × $10/M + 0.1M × $50/M = $15.00
route = 20% × $15.00 + 20% × $3.00
      + 40% × $3.20 + 20% × $0.15 = $4.91
overhead = 5% × $15.00 = $0.75
total = $4.91 + $0.75 = $5.66
saving = 1 - $5.66 / $15.00 = 62.3% (rounded)
```

按 Codex token 费率，同一算例是 **375 → 141.5 credits**。这不代表订阅月费减少 62.3%，也不能直接换算成每周可用额度增加多少。

20% / 20% / 40% / 20% 和 5% 都是预算假设，不是固定分配比例，也不是用户样本的平均值。实际任务如果频繁返工，可能比全程使用一个模型更贵。小任务直接做，不开子代理，也就没有这部分路由带来的节省。

## 计算方法与当时的计费备注

逐模型相加：

```text
cost = uncached_input × input_rate
     + cached_input × cached_input_rate
     + output_including_billed_reasoning × output_rate
     + applicable_cache_write_and_tool_fees
```

再拿同一任务的总费用、完成质量和耗时比较。实际日志已经包含规划、检查和返工时，不要额外再加一次示例里的 5%。

- API 缓存写入通常按输入费率的 1.25× 计费；Codex credits 不单列缓存写入费。
- GPT-6 Fast mode：API 是适用 Standard 费率的 2×，Codex credits 是 2.5×，不能混用。
- 超长上下文、缓存比例、输出量、重复上下文和返工都会改变结果。
- 少数仍使用旧 rate card 的 Enterprise 工作区，以实际适用费率为准。

## v1.0 历史价格 / Historical rates · 2026-08-04

以下保留旧版算法。基线是全程 GPT-5.6 Sol，**不适用于当前 Sol 6.1 候选配置**，也不和 Ponytail 上游公布的数字叠加。

### API · 每 1M tokens / per 1M tokens

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | $5.00 | $0.50 | $30.00 |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 |
| GPT-5.6 Luna | $0.20 | $0.02 | $1.20 |

### Codex credits · 每 1M tokens / per 1M tokens

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | 125 credits | 12.5 credits | 750 credits |
| GPT-5.6 Terra | 50 credits | 5 credits | 300 credits |
| GPT-5.6 Luna | 5 credits | 0.5 credits | 30 credits |

当时同类 token 的相对费用均为 Sol = 1.00、Terra = 0.40、Luna = 0.04。

| 场景 / Scenario | 示例分配 / Token shares | 额外开销 / Overhead | 预计节省 / Estimated saving |
| --- | --- | ---: | ---: |
| 普通明确型 / Clearly scoped | Sol 10% · Terra 20% · Luna 70% | 3%–7% | 72.2%–76.2% |
| 混合型 / Mixed | Sol 20% · Terra 40% · Luna 40% | 2%–12% | 50.4%–60.4% |
| 复杂型 / Complex | Sol 25% · Terra 60% · Luna 15% | 7%–17% | 33.4%–43.4% |

```text
route_cost = sol_share × 1.00
           + terra_share × 0.40
           + luna_share × 0.04
           + orchestration_overhead
saving = 1 - route_cost

ordinary_route_cost = 0.10 × 1.00 + 0.20 × 0.40 + 0.70 × 0.04
                   + (0.03 to 0.07)
                   = 0.238 to 0.278
ordinary_saving = 72.2% to 76.2%
```

它们是不同假设下的区间，不是所有任务的固定收益，也不能合成一个“平均节省 56%”。当时的参考入口：[OpenAI model comparison](https://developers.openai.com/api/docs/models/compare)、[Codex rate card](https://help.openai.com/en/articles/20001106-codex-rate-card)。这些页面会更新，以上数字保留的是当时快照。

## English

The tables retain two historical price snapshots, not current quotes. **2026-09-26** describes v1.1.0's four-model setup, not this Sol 6.1 candidate. The candidate has no measured savings claim. The historical rates are per 1M tokens, Standard mode, with no more than 272K input tokens in a request. The total 1M input in the example can span multiple requests.

### The historical v1.1.0 README example

Assume 1M uncached input and 0.1M output tokens in total. Split each token category **Astra 20% / Sol 20% / Terra 40% / Luna 20%**, then add **5% of the all-Astra baseline** for coordination.

The all-Astra baseline is **$15.00**. The weighted model cost is **$4.91**, plus **$0.75** overhead, giving **$5.66**, or **62.3% less** after rounding. The equivalent Codex token-rate calculation is **375 → 141.5 credits**.

Those shares and the 5% overhead are assumptions for a budget, not routing quotas, observed averages, or a guarantee. The example excludes human effort and elapsed time, tool fees, and caching. It does not establish equal output quality across models. Rework can make a run more expensive, and tasks done directly without delegation have no routing savings.

API dollars and Codex credits are different billing units. Neither result means your subscription price falls by 62.3%, nor does it directly establish an increase in included weekly usage.

### Calculation method and historical billing notes

For each model, add uncached input, cached input, and output including billed reasoning at their respective rates, plus applicable cache-write and tool charges. Compare the same task's total cost, quality, and elapsed time. If the logs already include planning, review, and retries, don't add the example's 5% again.

- API cache writes are generally 1.25× the input rate; Codex credits have no separate cache-write charge.
- GPT-6 Fast mode is 2× applicable Standard API rates, but 2.5× for Codex credits.
- Long context, cache use, output volume, repeated context, and retries affect the total.
- Some Enterprise workspaces still use a legacy rate card; use the one that actually applies.

In that snapshot, Sol and Terra had the same input price; Sol had the lower output price. The old Terra routing was not proof that it always cost less. Check applicable live rates before estimating a new run.

### Older calculations

The **2026-08-04** tables describe v1.0, with GPT-5.6 Sol as the baseline and relative prices of **1.00 / 0.40 / 0.04** for Sol / Terra / Luna. The three historical scenario ranges are **72.2%–76.2%**, **50.4%–60.4%**, and **33.4%–43.4%**.

They do not apply to the current Sol 6.1 candidate, represent a fixed average, or add to Ponytail's upstream results. The historical formulas and prices are kept above so they can still be checked and reproduced.
