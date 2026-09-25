# Orchestration protocol

Read for Assist planning or coordinated execution, not for ordinary Direct work.
Use the user's requested outcome as the boundary; a Skill does not add scope.

## Plan and schedule

For one decision, return a recommendation and acceptance criteria in prose.
For coordinated work, use the smallest useful graph. Equivalent concise formats
are valid; field spelling is not a safety boundary.

```yaml
goal: "User outcome"
done_when:
  - id: REQ-1
    criterion: "Observable requirement"
    evidence: "Falsifiable check"
tasks:
  - id: task-a
    task: "Bounded action"
    requirements: [REQ-1]
    agent_profile: efficient
    dependencies: []
    read_scope: ["needed/path"]
    write_scope: ["owned/path"]
    do_not_touch: ["excluded/path and side effects"]
    expected_result: "Observable result"
    verification: "Procedure and passing condition"
    required_evidence: "Output or artifact tied to the candidate"
    can_launch: true
    held_reason: null
stages:
  - [task-a]
integration_owner: host
```

Assign each Requirement ID to a task or the Host. Planning may use zero workers.
Select each worker directly; no task must visit every tier:

| Profile | Default | Assignment boundary |
| --- | --- | --- |
| controller | Astra / high | Sole planning, architecture, arbitration, and final review owner; keep hard inseparable decisions here. |
| specialist | Sol / high | Difficult but independently contractible reasoning, root-cause diagnosis, implementation, or targeted read-only review. |
| complex | Terra / high | Regular implementation, routine debugging, tests, and integration under settled requirements; the ID is retained for compatibility. |
| efficient | Luna / max | Mechanical batches with explicit transformation rules, little judgment, and objective checks. |

Terra is the normal implementation choice when delegation helps. A tiny edit or
one command stays Direct; a large deterministic batch may suit Luna. Sol is not
a mandatory reviewer or a second scheduler. An unclear overall goal or tightly
coupled architecture remains with Astra until a useful task can be separated.
Do not split work simply because there are many files or launch a worker just
to demonstrate that its model is available.

Delegate when a bounded handoff enables useful independent progress, contains
bulky exploration, or supplies needed independent scrutiny. Complexity alone is
not a reason. Batch related same-rule edits under one owner. While a worker owns
a task, the Host does separate integration or prerequisite work, not a duplicate
implementation or investigation. Inspect the handoff instead of replaying it.

Launch the minimum sufficient dependency-ready frontier, usually 1–3 workers,
within **live capacity**, accounting for the Host, controller, and other active
agents. Queue the remainder. Dependent tasks run sequentially or in waves.
Parallel writes need disjoint files, components, shared state, and side effects.
Shared configuration, migrations, generated outputs, and lockfiles need ownership
too. If an overlap is uncertain, serialize.

Capacity waiting is not BLOCKED or a new approval gate. When no independent work
remains, use the runtime's completion wait rather than repeated short polls;
keep user progress updates separate from worker-status polling. Do not take over
an active worker's task merely to avoid waiting.

## One active owner

Take a baseline of the actual worktree, including pre-existing user changes and
untracked files. Give each write scope one owner at a time. Multiple read-only
opinions may run concurrently; the controller chooses one implementation.

Ownership may transfer, even after edits, only when:

1. The previous worker is stopped and all its mutating command processes have
   ended. A timeout or an interrupt request alone does not prove quiescence.
2. The Host inspects and preserves the actual diff and unrelated user changes.
3. The new owner receives the current candidate, prior attempts, and exact scope.
4. Affected verification is rerun on the eventual final candidate.

Never let a replacement race an old writer. Do not reset, restore, clean, or
overwrite user changes to make a handoff easier. Stop the affected write path
when a safe handoff cannot be established; independent safe work can continue.

## Worker packet

Required semantics: objective, authorized read/write boundary, expected result,
and a falsifiable verification with required evidence. Include dependencies or
stop conditions when applicable. IDs help multi-part work, but a missing heading
or optional field is not BLOCKED.

```text
Task ID / Requirement IDs: task-a / REQ-1
Task: One bounded objective
Context: Relevant inputs and prior evidence only
Read scope: Exact paths needed
Write scope: Exact owned paths, or [] for read-only work
Do not touch: Excluded paths, user edits, and side effects
Dependencies: Completed prerequisite outputs, or None
Expected result: Observable acceptance condition
Verification: Command/procedure; passing condition; required evidence
Stop conditions: Actual scope, safety, or authorization boundary
```

Do not copy the full conversation into the packet. Workers preserve others'
edits, stay inside scope, do not redesign the overall run, and do not delegate.
Repair missing metadata from existing context. Unclear authority or conflicting
write ownership must be resolved with the controller before the affected action,
not guessed. Only the Host asks the user for genuinely missing authority.

## Minimal implementation — adapted from Ponytail

This is a brief judgment check during existing planning, execution, and review,
not another phase or a requirement to read the whole repository.

Understand the affected flow and relevant callers first. Then choose the simplest
approach that meets the complete requirement:

- Search the relevant authorized scope for an existing implementation before
  writing one. Reuse a suitable helper; if it is unsuitable, name the concrete
  mismatch instead of quietly duplicating it.
- Prefer suitable standard-library, platform, or already-installed capabilities.
- Add only the implementation or dependency genuinely missing; avoid speculative
  layers, configuration, frameworks, and “for later” abstractions.
- Fix the cause at the correct boundary, not only one visible symptom.
- Keep readable code and the necessary validation, error handling, accessibility,
  compatibility, and regression checks. Do not optimize for one-line code or LOC.
- A simplification must not silently replace an explicitly requested feature.

The controller can note a concrete unnecessary addition while reviewing the real
diff; it does not launch a separate simplification reviewer. No sweeping cleanup
of unrelated existing code. Attribution and the upstream MIT terms are retained
in [ponytail-license.txt](ponytail-license.txt); upstream benchmark results are not
PROVE results.

## Results and verification

A worker returns enough to verify the task; equivalent prose is acceptable:

```text
Task ID: task-a
Status: PASS | FIX | BLOCKED
Summary: Result or concrete failure
Inspected / Changed: Exact paths, or None
Requirement coverage: Assigned requirements and supporting evidence
Verification: Actual procedure, output, exit status / observation
Evidence: Candidate identity and inspectable artifacts
Assumptions / Risks: Material uncertainty, or None
Failure class: runtime | timeout | model_identity | permission | dependency | scope | verification | evidence_quality | conflict | none
Blocker: Concrete missing capability/authority, or None
```

Transport `completed` is not acceptance. If output is missing, request a
result-only follow-up (no new writes), inspect actual files, or run the missing
check inside existing authority. A summary with no evidence is not PASS, but it
does not automatically block the entire run.

Bind evidence to the reviewed candidate (commit plus diff, or an exact relevant
file snapshot). After a change, invalidate affected evidence only. Inspect the
actual diff before accepting claimed paths; before/after snapshots show net
changes, not who wrote them or proof that no temporary write occurred.

The controller reviews the original request, real files/diff, verification,
requirement coverage, and finally worker summaries. **Verify the verifier**:
right candidate, right requirement, meaningful passing condition. File existence,
tautologies, skipped tests, wrong scope, or unexpected check-induced mutations
do not justify success. Use focused existing tests; broaden only when risk or
shared behavior calls for it. Do not add a test framework just to satisfy a form.

Ordinary work needs no extra challenge call. A specific high-consequence risk,
uncertain root cause, or conflicting evidence may justify one bounded read-only
challenge. Judge consequence separately from implementation difficulty: even a
small authorization change can merit scrutiny. If independent review is needed,
use a fresh context that did not implement the candidate, supply the original
requirements and actual diff, and keep the reviewer read-only. It produces
evidence, not a second controller or automatic approval.

## Recovery and final review

Distinguish FIX (work remains) from BLOCKED (no safe next action). A failing
test, a missing result heading, or a useful second correction is normally FIX.

A Correction Packet can be brief: failed requirement, Failure class, exact
evidence, same-scope Delta, and the check that must pass. Fix the packet before
retrying; a new attempt needs a changed hypothesis or meaningful new evidence.
A worker may repair and rerun within its existing task authorization. The
controller may reassign a mechanical task to Terra or a difficult independent
unit to Sol when new evidence warrants it. Skip intermediate tiers when they
add no value; do not require a failed lower-tier attempt first. Astra retains
inseparable decisions. Use the safe handoff above, not a new user approval.

Track consecutive no-progress attempts. Stop that path after two, or earlier
on a user limit, exhausted budget, safety boundary, or no safe next action.
The controller can choose a genuinely different safe approach within scope;
escalation and resume must not erase attempt history or disguise identical retries.
Report a true blocker only after safe alternatives are exhausted.

```yaml
verdict: PASS | FIX | BLOCKED
requirements_coverage:
  - requirement: REQ-1
    status: satisfied | unsatisfied | blocked
    evidence: "File, diff, command output, or artifact"
findings: []
required_fixes: []
residual_suggestions: []
evidence_quality: sufficient | insufficient
remaining_risks: []
```

PASS requires all requested criteria supported by current evidence. Keep optional
improvements separate. A plan is not a stop point in authorized implementation.
A status inquiry does not revoke authorization. New destructive/external actions,
consequential unresolved choices, or actual permission boundaries still require
the Host to stop and obtain direction. Cite the specific constraint, not a generic
“protocol requires approval.”

For long/interrupted work, a resume packet records goal, completed evidence,
in-flight tasks, ownership, candidate_identity, attempts, artifact_location, and
next_action. Reconcile it with the live workspace; never redispatch completed
work or reset attempt history.
