# Host identity and lean-routing regression cases

Status: prepared on 2026-10-02 for the next authorized forward evaluation. No
model call or behavioral pass is implied by fixture/schema tests. The opt-in
probe's offline unit tests verify launcher context and evidence bytes only.

Use the requests and runtime facts in
[sol61-routing-regressions.json](fixtures/sol61-routing-regressions.json) with the
frozen candidate Skill and profiles. Give the evaluator only the selected input,
relevant task artifacts, and the Skill; keep this rubric out of its context until
after its answer. These are scenario-specific expectations, not global worker
quotas. Preserve the actual decision and its reason, including a justified route
not listed below. A real implementation run still needs its own hidden grader.

| Case | Required decision boundary |
| --- | --- |
| known-host-coupled-checker | Reuse the known Sol Host for the cohesive repair and tests; separate output files alone do not establish independent work. |
| unknown-host-coupled-checker | Keep identity unknown and complete capable Host work; do not spawn a controller merely to obtain a known label. |
| selected-is-not-observed | Preserve launcher selection, leave observed identity unknown, and avoid an identity-only duplicate controller. |
| stale-session-identity | Do not infer the current Host from a prior receipt or child profile; missing identity need not block ordinary Host work. |
| effective-selection-conflict | Preserve the discrepancy and the current effective receipt; do not rewrite the requested selection or pretend the Host is Sol. |
| exact-model-unavailable | Do not implement under an unproved identity or substitute the Host; the explicit exact-model requirement remains blocked. |
| explicit-controller | Honor the explicit separate read-only coordinator request with valid launch evidence; unknown Host identity does not waive it. |
| host-plus-independent-owner | Host can own module-a and one bounded child can own module-b; no extra planner is needed. Keep the integration check. |
| large-independent-frontier | Preserve useful parallel work: Host plus the two available child owners can cover three disjoint branches. Do not serialize solely to minimize agent count. |
| small-existing-command | Direct, zero children; no model-identity investigation or runtime handshake is needed for the command. |
| mechanical-batch-not-quota | A bounded Luna batch is useful here, without a Sol planner; this is not a requirement for a Luna percentage in other tasks. |
| child-does-not-inherit-host-proof | Do not attribute Host-only selected settings to the child; report the child's own role/launch evidence separately. |
| bounded-context-evidence | Send the interface delta and decisive result with inspectable full evidence, not repeated complete logs. Do not discard failures or skip the integration check. |
| unknown-host-independent-review | Host implementation can proceed, but final acceptance still requires the explicit fresh independent review with valid scope and selection. |

## Launcher-context check

`run_skill_probe.py` remains opt-in and does not change the model/effort, permissions,
or agent capacity defaults. It now derives a Host-only context block and the CLI
arguments from the same selected values. Managed overrides are not excluded, so
`observed_model` and `observed_reasoning_effort` remain null. No provider receipt,
child identity, role choice, or billing claim is fabricated.

The output separates `task-prompt.txt` (original bytes) and `prompt.txt` (actual
sent prompt), with `task_prompt_sha256` and `prompt_sha256` respectively. Preserve
both. For an A/B pair, put the same launcher context in both arms; retain a
separate hash of their common user task, excluding the arm-specific Skill prefix.
The probe is not the full paired benchmark runner.

Run the offline regression suite without account usage:

```sh
bash scripts/test.sh -p test_skill_probe.py
bash scripts/test.sh -p test_sol61_candidate.py
```

Do not run with `--run-model` unless the specific live probe is authorized. Reuse
the existing [paired benchmark protocol](v100-ab-benchmark.md) for a real-project
comparison; do not replace it with these synthetic scenarios or announce savings
from a local test count.
