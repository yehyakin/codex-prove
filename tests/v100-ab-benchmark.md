# v1.0 matched A/B benchmark protocol

This protocol compares the published v0.4.1 baseline with the evidence-first
candidate. It contains no performance result and declares no winner.

## Integrity rules

- Use the same user prompt, base commit, tools, permission boundary, time limit,
  Host model settings, and verification commands for both arms. Skill instructions
  may differ; `prompt_sha256` hashes the common user task, not the arm-specific
  Skill prefix. Preserve both complete prompts separately.
- Export each cell into a fresh isolated checkout without future Git objects or
  remotes that reveal the target patch.
- Keep the grader unavailable to the agent until the run ends. Record hashes for
  the prompt, grader, manifest, base commit, and final candidate.
- Run each case at least three times and use the counterbalanced schedule emitted
  by `benchmark_ab.py`.
- Record unavailable token or cost telemetry as unavailable in the capture
  adapter; never invent or convert accounting units. A result file submitted to
  this harness must contain complete comparable cells.
- Calibrate each hidden grader before paid runs: the known-bad base must fail and
  a reference-good candidate must pass.

## Cases

The manifest covers Direct routing, parallel disjoint work, missing requirement
evidence, a wrong-scope verifier, a high-risk selective challenge, interruption
resume, dirty-worktree preservation, and timeout ownership.

## Metrics

Quality and integrity:

- held-out pass;
- integrity pass;
- false PASS rate.

Efficiency:

- input and output tokens;
- elapsed seconds;
- cost value and its original unit;
- subagent count;
- retry count.

Resource savings count only when the cell passes both held-out and integrity
checks. Descriptive output is not a release claim until the complete run bundle
is independently auditable.

## Commands

```sh
python3 scripts/benchmark_ab.py validate tests/fixtures/v100-ab-benchmark.json
python3 scripts/benchmark_ab.py schedule tests/fixtures/v100-ab-benchmark.json --output schedule.json
python3 scripts/benchmark_ab.py summarize tests/fixtures/v100-ab-benchmark.json results.json --output summary.json
```

The tool does not launch Codex or any model. A separate authorized runner must
execute the frozen cells and capture measured results.

## Routing scope and accounting

The legacy protocol defaults to `routing_scope: fixed_settings`. Its summary is
not evidence of autonomous mixed-model routing. An autonomous protocol must set
`routing_scope: autonomous` and `routing_unconstrained: true` before freezing:
review the complete prompts and runner configuration to establish that neither
forces Solo, prohibits agents, or forces a worker model. This declaration is a
review requirement; the harness cannot prove prompt semantics from hashes.
Freeze the Skill and role profiles by content hash, keep the same task and hidden
grader, and let each arm choose its own route. Record the actual chosen route and
model launches even when it chooses Direct or Solo. Do not embed the target patch
or reference solution in either implementation context.

Make Host metadata visibility symmetric: the launcher may supply the explicit
model/effort it actually selects to both arms, scoped to the current Host, with
unobserved effective settings left unknown. Derive that context from the same
values used to launch, not user-config defaults or a prior session. Keep this
selection distinct from runtime receipts and child selections. An arm's ignorance
of its own model must not be an artificial reason to force a separate controller.
Preserve both the common user task and full sent prompts with separate hashes;
the optional `run_skill_probe.py` demonstrates this capture but is not an A/B runner.

The probe's `usage_scope: root_cli_stream_only` covers only its supplied CLI
completion records. `whole_run_usage` is always null: retained transcripts alone
do not discover descendants or prove their costs were captured. The parser
deduplicates explicit turn identities or native `turn.started` boundaries;
ambiguous/conflicting records remain unknown. After a failure, unfinished turn,
timeout, or nonzero process exit, `usage` is null; `observed_completed_usage`
can retain the known successful subset, never the missing bill. Completeness
applies only to this declared scope, not to provider billing or the full tree.
Use the separately reconciled per-session raw records for end-to-end accounting;
do not feed root-only probe totals into a whole-run comparison.

Each parser input must be one intact CLI invocation, not concatenated exports or
resume logs. Repeated `thread.started` or invalid event types invalidate the
total; an ended failed turn can retain a later successful subset without claiming
the missing failed usage. Ordinal boundaries are not globally unique IDs and
cannot authenticate edited/reconstructed logs. Preserve original file hashes and
authoritative session/turn records for multi-invocation or full-tree accounting.

The harness rejects paired base/task/grader mismatches, nonfinite metrics, and
numeric overflow in aggregate metrics. It rejects different cost units across
arms. If any run lacks cost telemetry, that arm's total remains null;
`cost_observed_runs` reports coverage. It never replaces missing accounting with
zero or declares a winner. `autonomous_routing_declared` reports only the frozen
manifest's declaration, not verified runtime behavior.

For raw capture, retain run/thread/turn IDs, role, requested and observed model,
reasoning effort and service tier, config hashes, failures, retries, recovery,
and raw usage. Mark unobserved fields unknown. Count each authoritative completed
turn once by run/thread/turn identity; identical duplicate exports are one event,
conflicting duplicates need investigation. Do not sum cumulative snapshots with
completed totals, or add parent aggregates to children they already include.
Input includes cached input and output includes reasoning output: subtract cached
input once when pricing, never add reasoning output again. Cached input is not
free. Preserve attempts with no reported usage as unknown, including startup
failures. Report Host/coordinator coverage separately; missing Host usage prevents
an end-to-end claim. API equivalent estimates need explicit dated prices and
units; they do not establish subscription cash or quota savings. Compare cost
only alongside equivalent held-out quality, integrity, and failure coverage.
