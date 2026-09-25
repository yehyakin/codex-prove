# Forward validation

Date: 2026-09-05. Candidate: v1.1 development.

## Separate specifications from execution evidence

`fixtures/forward-cases.json` contains **49 scenario specifications**. Unit tests
check their structure and selected contract invariants; they do not execute 49
model conversations. Do not publish that count as 49 live-model passes.

The automated suite also runs actual isolated installer transactions, migration,
rollback, uninstall/restore, and preservation of unrelated files/configuration.
POSIX tests use temporary `ORCHESTRATE_HOME` roots. Windows execution belongs to
the existing PowerShell CI matrix, not a macOS structural check.

Live model probes and their limitations are recorded in
[the v1.1 audit](../docs/release/v1.1-gpt6-audit.md). They use disposable fixtures,
fresh agent contexts, exact model/effort selection, real outputs, and actual
candidate inspection. No business repository or production system is modified.

## Scenario coverage

| Area | Required outcome |
| --- | --- |
| Ordinary or explicitly invoked tiny edit | Direct, zero child-agent delegation |
| Difficult indivisible analysis | Controller Assist, workers optional |
| Difficult independent unit | Sol specialist, no required lower-tier failure |
| Regular implementation with settled interfaces | Terra, no routine extra reviewer |
| Large mechanical batch with explicit rules | Luna when delegation helps; one cheap command may stay Direct |
| Specialist review-only request | Empty write scope, no implementation of its own findings |
| Independent modules | Smallest useful ready frontier within live capacity |
| Capacity full, worker still verifying, user wants speed | Wait for completion; no duplicate writer or renewed approval |
| Many same-rule edits | One useful batch, not an agent per file |
| Tiny change with serious security consequences | Risk-sensitive evidence; fresh read-only context if independent review is needed |
| Shared file/configuration | One active writer; serialize overlap |
| Database → API → UI | Dependencies determine waves |
| Packet heading missing but scope/check already known | Repair metadata internally |
| Scope or new authority genuinely unknown | Hold the affected action; resolve safely |
| Worker PASS without evidence | FIX; inspect artifacts or run missing verification |
| Candidate changed after verification | Rerun affected checks, retain unaffected evidence |
| Host selection known, child metadata hidden | First-turn task allowed; no self-attestation gate |
| Stale custom role, exact generic selection available | Record explicit-profile launch, not custom-role success |
| Required exact model cannot be selected | No impersonation or hidden substitution |
| Nested dispatch unavailable | Host-mediated Compatibility |
| Partial edit needs a different executor | Stop old worker and mutating processes, preserve diff/history, then hand off |
| Timed-out writer may still mutate | Do not start a racing replacement |
| A useful second correction | Continue inside existing authorization |
| Repeated no-progress or exhausted user budget | Stop that path and reassess; do not reset attempts |
| Missing original requirement | Controller finds the gap in real candidate evidence |
| Ponytail-inspired implementation | Inspect scoped existing capabilities before adding code |
| Minimality conflicts with security or explicit behavior | Keep the guard and required behavior |
| User changes and interrupted work | Preserve edits, reconcile state, do not repeat completed work |
| Explicit cancellation or redirection | Stop/replan; a status question alone does not pause |

## Live-probe method

1. Build a fresh fixture directory with a stub, nearby reusable helper, and
   falsifiable tests. Keep input fixtures separate from prior generated answers.
2. Give the evaluator the actual user request, current source Skill/profile,
   scope, and raw fixture. Do not tell it the intended implementation or prior
   outcome.
3. Inspect actual files and test output independently. A successful functional
   test does not prove the minimal-implementation policy was followed.
4. For review, supply the complete original requirements plus candidate and
   worker evidence. A deliberately incomplete worker packet tests whether the
   controller can find an omitted requirement.
5. Apply only observed, narrow instruction corrections; run a fresh-context probe
   and retain the first result as well. Avoid an unbounded prompt-tuning loop.
6. Treat short probes as behavioral evidence, not matched A/B cost, latency,
   quality, or general reliability measurements.

## Development-only worker pilot

`worker_model_pilot.py` compares Sol 6 high and Terra 5.6 high using identical
regular-worker instructions. Three synthetic maintenance fixtures, three repeats
per model, fresh directories, counterbalanced serial calls, and external checks
are separate from the full v1.0 A/B benchmark. Graders must reject the known-bad
baseline and pass the reference implementation before any model call.

Run free calibration with Python 3.11+ and a new output directory outside this
checkout: `python3 tests/worker_model_pilot.py --output /tmp/prove-pilot-calibration`.
`--run-models` explicitly enables 18 account-usage calls; `--codex` selects the
installed CLI path. Logs, commands, hashes, partial failures and candidates stay
in that directory. No automatic retry or model fallback. Live calls currently
require macOS: post-run checks deny writes, network and reads under `/Users`,
without inherited secrets or user Python startup. Offline oracle calibration
supports POSIX. This pilot is not part of the installed Skill or Windows installer.

Ordinary CI tests only the offline grader controls and evidence handling. Missing
usage/cost is unknown, not zero; cached input is a subset of input, not additional
input. CLI elapsed time includes startup and tools. This small pilot cannot
establish workflow savings, general superiority, or Desktop custom-role behavior.

Historical v1.0 benchmark manifests, release evidence, and the old
`fixtures/v040-baseline-red.md` remain history. Existing recovery/evidence cases
may start from an already assigned efficient worker; they are not defaults for
classifying new tasks. Their immutable-owner and
one-correction expectations are not the v1.1 recovery contract.
