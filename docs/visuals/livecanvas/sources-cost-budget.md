# Cost budget: all-Astra baseline

As of 2026-10-01 (Asia/Shanghai). This is an illustrative budget, not a measured result.

[Official Codex credit rates](https://learn.chatgpt.com/docs/pricing) were opened and read on this date. The Standard token-rate cells are preserved in [the numeric extract](evidence/cost-budget-rates.json). Rates are credits per million tokens; API USD prices and included subscription allowances are not used.

For 1M uncached input and 0.1M output including billed reasoning: Astra costs 375 credits, Sol 6.1 costs 75, and Luna costs 3.75. The same 80% Sol / 20% Luna shares apply to both input and output. They are hypothetical shares, not measured usage or fixed quotas.

```text
all_astra = 1 * 250 + 0.1 * 1250 = 375
all_sol = 1 * 50 + 0.1 * 250 = 75
all_luna = 1 * 2.5 + 0.1 * 12.5 = 3.75
routed = 0.8 * 75 + 0.2 * 3.75 = 60.75
extra = 0.05 * 75 = 3.75
total = 60.75 + 3.75 = 64.5
cost_ratio = 64.5 / 375 = 17.2%
saving = 1 - 64.5 / 375 = 82.8%
```

The 3.75-credit extra budget is 5% of all-Sol, or 1% of all-Astra. Changing the comparison baseline does not increase that assumed overhead to 5% of Astra. It stands for additional coordination/review/retry cost and must not be added again when already present in real usage.

No cache discounts, tool/image fees, labor, latency value, equal-quality guarantee, subscription fee savings, or weekly allowance expansion are claimed. Different real token volumes or rework can change the result. Current candidate cost notes still report no complete same-task A/B result; the 8 project claims and committed excerpts in data-cost-budget.json retain that boundary.

Equal-sized visual cards identify two plans; area and connector motion do not encode a numeric ratio or measured speed. All numeric text and the illustrative disclaimer remain visible throughout the animation. The old nonnumeric mechanism assets remain unchanged under the cost series.
