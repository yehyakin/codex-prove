# Sol 6.1 live Compatibility smoke

Date: 2026-09-30. Candidate branch: `codex/sol61-lean-routing`.
Status: **PASS for this fixture's REQ-1…6**, including independent review and
the original controller's final files/diff/evidence acceptance.
This is a bounded synthetic-project check, not release approval or a benchmark.

## What actually ran

The Host selected three fresh generic contexts with exact
`gpt-6.1-sol`, `high`, and `fork_turns="none"`: one controller, one implementation
worker, and one independent read-only reviewer. Each received the relevant
candidate profile instructions. The launch arguments were accepted and the
contexts used real local tools; model identity was not inferred from their names
or self-description. The controller was reused for final acceptance.

The current chat's custom-role mappings were older than the candidate. These
were therefore **explicit-profile launches**, not proof of new-session discovery
or selection of the candidate's custom role IDs. Broader inherited tool capability
remained available; file ownership and read-only review were operational scopes,
not demonstrated OS sandbox isolation. The Host's model/effort are not asserted.

The harness deliberately selected Compatibility and plan-first for this exercise.
Its result does not establish the default route or optimal coordination overhead.

## Fixture and observed execution

The disposable project is `/tmp/prove-sol61-live-3a2fx7`. It implements an offline
JSON-to-CSV report with exact-team selection, count validation, aggregation,
Unicode/CSV escaping, a top-level catalog key migration, and CLI error handling.
Frozen request/checker files and a pre-existing synthetic user note must survive.

| Stage | Actual owner and evidence |
| --- | --- |
| Direct | Host changed fixture metadata and checked it before any agent launch. |
| Planning | Sol controller read the original request and checker, assigned disjoint ownership, and identified missing edge-case coverage. |
| Parallel work | Sol wrote only `records.py` while Host handled `render.py` and four tiny catalogs. This was Host + Sol, not two Sol execution workers. |
| Integration | Host alone implemented `report.py` after the components passed. |
| Independent review | A fresh Sol context inspected the final files/diff and added discriminating read-only probes. It found no actionable defect. |
| Missing evidence | The same reviewer supplied its previously executed inline source in a result-only follow-up. No new review context or implementation was started. |
| Acceptance | Original controller read real files/diff, checked the verifier and snapshot/output binding, and returned PASS for REQ-1…6 without repeating equivalent tests. |

The controller kept the small mechanical batch on the Host; no Luna call was
needed for this fixture. It chose fresh Sol for the ordinary requested independent
review, not Astra. Neither omitted model is counted as tested.

## Checks and evidence

- The unimplemented selection probe initially failed with `NotImplementedError`.
- Final frozen fixture suite: **12 distinct test methods passed**, exit 0.
  Repeated runs of those methods are not additional test cases.
- Additional review probes passed: exact/case/whitespace/prefix team exclusions,
  input purity, invalid selected rows, all 12 catalog/team subprocess combinations,
  late failures without partial stdout, import behavior, and quoted newline output.
- Malformed file contents and permission/decoding failures used in-memory
  `Path.read_text` mocks. They were not on-disk failure-injection tests.
- The probe labeled CR “roundtrips” checks exact quoted output; the catalog
  subprocess probes perform CSV parsing. The label is not a stronger assertion.
- The saved probe was replayed successfully to verify the exported evidence script.
- Frozen request/checker files, the pre-existing note, and completed metadata
  remained byte-identical. Fixture diff stayed
  `a9f3b315a4777dd1d32218ca3b34d04d0ca0161c2631ecca1b7f3869235f902c`.
- The 12 selected installed Skill/profile/config files had matching before/after
  SHA-256 values. Candidate runtime source and the v1.1.0 historical receipt were
  unchanged. No installation, source-repository commit, push, merge, or release
  occurred. Only the disposable fixture received a local baseline commit.

The [machine-readable receipt](sol61-live-smoke.json) contains accepted selection
arguments, runtime-source hashes, complete baseline/final fixture file contents,
file hashes, the real diff, and checker outputs/exit status. The
[additional review probe](sol61-live-review-probe.py) preserves the executed code.

To repeat the saved checks while the temporary fixture exists:

```sh
cd /tmp/prove-sol61-live-3a2fx7
/opt/homebrew/bin/python3.13 -B verify.py all
/opt/homebrew/bin/python3.13 -B - < /Users/kin3/Projects/codex-prove/tests/artifacts/sol61-live-review-probe.py
```

If that directory is gone, the receipt retains its complete baseline and final
files. Restoring them and rerunning checks is a new verification run, not a replay
of the recorded model calls. Catalog checks expect the baseline files in Git HEAD.

## Still unverified

Unforced Solo routing; two parallel Sol execution workers; candidate Luna/Astra
paths; fresh-session custom-role discovery and global candidate installation;
Native Nested; Windows execution; ownership-conflict and timeout/cancellation
fault injection; paired repeated quality, latency, token, or currency-cost tests.
Usage/currency totals are unknown, not zero. No savings percentage is claimed.

The repository's separate **122-check** packaging/install/regression suite passed
in an isolated source copy excluding unrelated untracked `media/` dependencies.
Those checks and the earlier 20 simulated routing cases are not additional live
model passes. Skill Creator validated both entrypoints; PowerShell execution
remains unverified because this host has no `pwsh`.
