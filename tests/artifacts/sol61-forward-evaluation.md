# Sol 6.1 candidate — current evaluator's simulated routing exercise

This is a fresh-context protocol exercise by the current evaluator, not a GPT-6.1 runtime validation. All routing, launches, checks, and outcomes below are proposals for the supplied cases. No simulated project work, child launch, model call, global configuration change, or project test was executed. No correctness score, cost comparison, or latency gain is asserted.

The complete inputs read were `SKILL.md`, `references/orchestration.md`, `references/runtime-notes.md`, all four `.codex/agents/*.toml` profiles, and `tests/fixtures/sol61-forward-inputs.json`. No other project documentation, tests, research, or history was used.

## Profile and counting conventions

| Alias | Child role ID | Selected model / effort | Operational write boundary |
| --- | --- | --- | --- |
| C | `prove-controller` | `gpt-6.1-sol` / `high` | Read-only |
| W | `prove-complex-worker` | `gpt-6.1-sol` / `high` | Assigned workspace scope only |
| A | `prove-specialist-worker` | `gpt-6-astra` / `high` | Read-only |
| L | `prove-efficient-worker` | `gpt-6-luna` / `max` | Assigned mechanical batch only |

Counts mean newly launched child contexts, not logical work items. Existing contexts are identified separately. A profile's configured model is not proof of an existing agent's actual identity.

For any proposed new child, send a complete bounded packet in a fresh context (`fork_turns="none"`), and check authoritative selection against its actual launch record. If custom-role mapping is stale but exact explicit selection is supported, use those exact settings and equivalent instructions, recording the explicit-profile launch and its actual permission boundary. Do not add an identity-only handshake. These cases do not demonstrate Native Nested operation; the proposals use Host launches and do not presume nesting support. Workers never delegate.

## Case decisions

### 1. `label`

- Route: Direct, despite the explicit invocation. The plain-text edit is small and low risk.
- Children: none; count 0. Keep the Astra/high Host.
- Ownership: Host alone writes `ui/button.txt` and accepts the result.
- Next: inspect the file, replace the label, then read the exact final content and actual diff. Require `Save changes`, preserving unrelated content and existing newline conventions. No graph, model probe, or full build is needed.

### 2. `existing-command`

- Route: Direct. The existing deterministic command makes this one short execution, not a reason to assign 800 items to Luna.
- Children: none; count 0. Keep the Sol 6.1/high Host.
- Ownership: Host runs the authorized generator, owns its fixture changes, and accepts.
- Next: establish the authorized fixture baseline, run the already-known normalize command and checker, and inspect full output, exit status, and the final diff. Confirm only the authorized fixture changed. The fixture gives no literal command strings, so none are invented here.

### 3. `matching-host`

- Route: Solo on the existing Host; one cohesive flow across several files.
- Children: none; count 0. Preserve the authoritatively selected `gpt-6.1-sol` / `medium`; the child profile's `high` default does not override it.
- Ownership: Host owns handler, serializer, and focused tests, plus acceptance. This is not independent review.
- Next: inspect the affected patterns and real baseline, define the preference's observable behavior, implement within that flow, then run the focused suite on the final candidate and inspect its diff and coverage.

### 4. `other-host`

- Route: Solo delegated to one complete-task owner. Investigation and implementation stay together.
- Children: one W; count 1, `gpt-6.1-sol` / `high`. No C or routine A.
- Ownership: W owns the import repair and malformed-row regressions. Astra/high Host owns acceptance and may do only separately authorized, non-overlapping release-note preparation.
- Next: record the worktree baseline and exact import/test scope, confirm the authoritative launch selection, and dispatch the full task with a meaningful malformed-row check and required evidence. Host later inspects the real final diff and results rather than duplicating W's investigation.

### 5. `analysis-only`

- Route: Assist; the request expressly ends before implementation.
- Children: one C; count 1, `gpt-6.1-sol` / `high`, read-only.
- Ownership: no project writer. C owns the comparative analysis and proposed acceptance criteria; the Luna/max Host accepts and delivers that analysis, not an implementation.
- Next: provide the two designs and relevant repository facts. Ask C to compare concrete consistency guarantees and failure scenarios, recommend one with supported tradeoffs, and identify a discriminating check. Do not launch implementation workers or create a development phase.

### 6. `independent-work`

- Route: Coordinated; three independent work items, with the Sol 6.1/high Host as the single controller.
- Children: two new contexts total: one W (`gpt-6.1-sol` / `high`) and one L (`gpt-6-luna` / `max`); maximum two active children. W handles module-a, then receives a new module-b packet in the same compatible context after completing its first assignment. L handles the catalogue concurrently. No extra C.
- Ownership: W exclusively owns the currently assigned module and its tests; L owns catalogue data and authorized checker outputs. Host owns integration and final acceptance. The second W assignment changes its explicit scope; it is not an overlapping writer.
- Next: baseline all three scopes, map requirements to the two execution streams, and verify disjoint side effects before dispatch. Require both module suites and the catalogue checker. Retain module-a's candidate-bound evidence when its files and dependencies remain unchanged during module-b work; perform any needed integrated check.
- Scheduling note: this is a deliberately small two-context schedule, not a claim that every module needs its own agent. A three-child schedule in waves could also fit the protocol, but must not launch all three into two free slots or assume an idle agent automatically releases capacity.

### 7. `serial-chain`

- Route: Solo on Host. Schema → adapter → demo dependencies are not independent workstreams.
- Children: none; count 0. Sol 6.1/high Host keeps the entire flow.
- Ownership: Host alone owns the local fixture schema, adapter, demo, and acceptance. Production remains excluded.
- Next: confirm the preserved original data and inspect the consumers, then implement sequentially in the existing context. Verify the final schema-to-adapter contract and the demo's use of the resulting data. Check for an actually runnable demo before proposing browser verification; do not substitute a claimed build for observed behavior.

### 8. `overlap`

- Route: Solo with one owner for both approved fixes. Speed does not make shared-file writes independent.
- Children: no new launch; count 0. The two available workers remain unassigned to these writes; their models/efforts are not supplied. Use the known Sol 6.1/high Host.
- Ownership: Host exclusively owns `shared/config.py` and the combined final candidate, then accepts it.
- Next: supersede the conflicting proposed scopes before either worker starts, inspect the baseline, and apply the two fixes serially under the Host's ownership. Check both requirements against the combined result. Since neither worker began, no edited-work handoff or process interruption is presently needed.

### 9. `authorization-change`

- Route: high-risk Solo execution with one bounded consequential independent review. The two-line size does not remove the security consequence.
- Children: one fresh A after the candidate is implemented; count 1, `gpt-6-astra` / `high`, read-only. It must not first help choose that candidate if its later review is to be called independent.
- Ownership: Sol 6.1/high Host is the sole writer and acceptance owner. A supplies findings, not approval. No deployment is authorized.
- Next: first conduct scoped read-only analysis, preserve the local baseline, and define cross-tenant denial plus legitimate same-tenant behavior as falsifiable checks. Implement the local condition and missing regressions; run final-candidate checks. Then give fresh A the original requirement, actual files/diff, and results for focused tenant-isolation scrutiny. If the reviewer needs a mutating test, return it to the authorized Host. Stop at any new production, credential, or enforceable-boundary requirement.

### 10. `advisor-independence`

- Route: Assist for the explicitly requested independent review; no implementation phase is implied.
- Children: one new A; count 1, `gpt-6-astra` / `high`, in a genuinely fresh context. Do not reuse the existing Astra strategist as the independent reviewer.
- Ownership: no writes in this review request. The existing Sol writer and its commands have ended. Host retains acceptance; A only advises. No new controller is needed.
- Next: provide the independent reviewer with original requirements, current candidate/files/diff, and final test evidence. Ask it to examine lock-order consistency and meaningful concurrency coverage using permitted non-mutating checks. Do not treat a different model name, or the previous advisor's new turn, as independence.

### 11. `missing-evidence`

- Route: continue the existing Solo evidence/recovery path, without launching another team or seeking new permission.
- Children: count 0 new; reuse the existing Sol worker. Its exact model generation and effort are not stated in this case; preserve/check its authoritative original selection rather than infer it from the current TOML.
- Ownership: the same worker retains its write scope for authorized corrections; Host owns acceptance. Its unsupported success claim is insufficient evidence.
- Next: first request the missing regression result as a result-only follow-up. If it was never run or cannot be tied to the current candidate, have that worker run it under the existing authorization, supply the full output and exit status, and repair any in-scope failure. Recheck only evidence affected by corrections; do not block on an optional result heading.

### 12. `unavailable-required-model`

- Route: intended Solo implementation cannot start because the user's exact model requirement is unavailable.
- Children: none; count 0. Do not launch the stale `prove-complex-worker` mapping to `gpt-5.6-terra` / `high`.
- Ownership: no implementation writer; Host owns the capability report, not acceptance of a substituted implementation.
- Next: report that exact `gpt-6.1-sol` / `high` selection is unsupported and preserve the unchanged workspace. Neither Host continuation, an older Sol/Terra launch, nor editing global provider settings satisfies the request. Continue only when the required capability exists or the user explicitly changes the exact-model requirement. The missing capability, not missing paperwork, is the blocker.

### 13. `optional-model-missing`

- Route: Solo on the authoritatively known Sol 6.1/high Host.
- Children: none; count 0. Unavailable Astra and Luna are irrelevant to this ordinary cohesive task.
- Ownership: Host owns implementation, checker execution, and acceptance.
- Next: inspect the relevant flow and baseline, implement using existing patterns, run the existing checker on the final candidate, and inspect its complete output and the real diff. Do not probe unused profiles, add an independent-review requirement, or pause for optional models.

### 14. `timeout-and-budget`

- Route: recovery/status reporting with a hard execution stop. The two no-progress attempts end that recovery path, and the exhausted budget disallows starting a different paid attempt merely because it is different.
- Children: none; count 0. Do not launch a replacement, specialist escalation, or retry. Existing worker/process liveness is unresolved.
- Ownership: `shared/config.py` must not be assigned to a second writer. Host owns safe reporting and preservation of already verified partial work; the uncertain old process has not been shown quiescent.
- Next: report verified completed portions separately, conditioned on their candidate identity and independence from the uncertain process. Use available read-only lifecycle/process state to determine what remains active; do not equate timeout, an interrupt request, or a net diff with process termination. Record the actual remaining ownership, two attempts, exhausted budget, preserved artifacts, and blocked write path. No new implementation can safely be promised under the supplied limits; any later handoff requires proven quiescence and the budget/authority issue to be resolved.

### 15. `dirty-worktree`

- Route: Solo on the Sol 6.1/high Host; a preservable user edit is not itself a blocker.
- Children: none; count 0.
- Ownership: Host is the single active writer for the file's requested export logic. The pre-existing timezone fix remains the user's change; Host accepts the combined candidate without claiming authorship of that fix.
- Next: reconcile the supplied baseline with the live file, patch only the distinct export logic, and inspect the final diff against both the baseline and request. Run the export checks and the supplied timezone regression on the final candidate. Do not reset, restore, clean, or overwrite the user edit to make the worktree tidy.

### 16. `integration-evidence`

- Route: continue the existing Coordinated acceptance pass after invalidating evidence affected by the integration edit.
- Children: count 0 new; reuse the existing read-only Sol controller. Its exact generation/effort is not given; retain/check its original authoritative selection rather than assert a new exact-profile launch.
- Ownership: Host owns the API-field integration edit and authorized test execution. The existing controller owns final evidence-backed review; Host consumes that review for delivery instead of repeating it. The controller remains read-only.
- Next: give the controller the actual field-name diff and current candidate. Run the affected module-a/module-b contract checks and a fresh cross-module check covering the changed field; the earlier integration result is stale. Preserve module-c's still-applicable evidence. The controller then reviews coverage and current artifacts once; do not accept the integration merely from earlier passing unit tests.

## Ambiguities and boundaries exposed by this exercise

1. **Configured roles versus existing runtime identities.** The supplied profiles consistently select Sol 6.1/high for C/W, Astra/high for A, and Luna/max for L. Cases with an existing “Sol” worker/controller do not specify its full identity or effort. The protocol correctly requires authoritative records; this exercise cannot upgrade those vague descriptions into exact-profile runtime evidence.
2. **High risk is an overlay, but route labels could be clearer.** Direct is explicitly zero-agent. A small security edit with an independent specialist therefore cannot be called unqualified Direct while also spawning A. Case 9 uses Solo plus the high-risk controls; the text could make this naming boundary more explicit.
3. **Minimum frontier does not determine a unique total child count.** In case 6, two contexts with sequential reuse and three logical work items satisfy the live two-slot limit. Separate children in waves are also possible. The protocol allows compatible context reuse but does not mandate one unique schedule; releasing an idle agent must not be assumed.
4. **Budget exhaustion and emergency quiescence are distinct.** The protocol clearly stops new work at exhausted budget and forbids racing writers. It does not specify a budget accounting mechanism or whether emergency process-stop operations are exempt. Case 14 therefore proposes no renewed implementation or paid retry and does not claim a process was stopped. Operational handling must use real runtime controls and authority, not a guessed exception.
5. **Existing controller authority is not always stated.** Cases 10 and 11 mention workers/advisors but no controller. Their proposals keep acceptance with the Host rather than inventing another controller. If an existing coordinated run were later evidenced, its sole controller would retain that responsibility.

No direct conflict in the four candidate model/effort mappings was found in the supplied text. None of these simulated decisions establishes model availability, sandbox enforcement, tool calling, live agent identity, successful tests, or acceptance of an implemented candidate.
