---
name: codex-prove
description: Use only when the user explicitly invokes $codex-prove for scoped model routing, parallel execution, and evidence-backed review.
---

# Codex PROVE

PROVE means **Planning, Routing, Ownership, Verification, Evidence**.
Use the least coordination needed to complete the user's request. This is a
workflow, not a guarantee of correctness. Do not invoke it implicitly;
ordinary small work stays Direct, including a small task with an explicit invocation.

默认用中文沟通。用户指定其他语言时从其要求；代码、路径和原始证据保留原文。

## Route before launching

- **Direct:** a clear answer, small edit, or deterministic command. The current
  Codex completes and checks it; zero agents, no graph or runtime handshake.
- **Solo:** one cohesive implementation or investigation, even across several
  files. Reuse a Sol 6.1 Host; otherwise, when the handoff is worthwhile, give one
  Sol worker the complete task. It plans, implements, and checks that task in one
  context. No separate planning agent; the Host accepts the real result.
  A self-contained mechanical batch may use one Luna instead, without a Sol planner.
- **Assist:** analysis or review only. Reuse a Sol 6.1 Host or ask one read-only
  Sol; for a named hard question or risk review use Astra. An explicitly required
  independent review starts with a fresh reviewer. Do not start implementation.
- **Coordinated:** at least two useful independent workstreams justify splitting.
  Reuse a Sol 6.1 Host as controller or launch one read-only controller; assign
  the smallest useful frontier. Dependencies alone do not justify more agents.
- **High risk:** start with scoped read-only analysis, recovery checkpoints,
  unique ownership, and explicit stop conditions. User authorization still governs
  destructive, production, credential-related, or irreversible operations.

Risk controls apply to every route: a one-line security change is not low-risk
merely because it is small. Direct does not waive required evidence or authority.
If a small edit needs a child reviewer, use Solo with risk controls, not zero-agent Direct.

Before delegated work, read [orchestration.md](references/orchestration.md).
Read [runtime-notes.md](references/runtime-notes.md) only when launching agents,
selecting Native Nested / Compatibility, or diagnosing a runtime failure.
Do not preload every reference for Direct work.

## Roles and authority

The TOML profiles select models and effort; role names stay model-neutral.

- **Controller (Sol 6.1 / high):** planning, ownership, arbitration, and final
  review for coordinated work. A separately launched controller stays read-only.
- **Regular worker (Sol 6.1 / high):** a complete Solo task or one independent
  module. Retains the `prove-complex-worker` ID; Terra is no longer the default.
- **Specialist (Astra / high):** one bounded difficult question or independent
  risk review, read-only. It advises; it neither schedules nor approves the run.
- **Efficient worker (Luna Max):** mechanical batches with explicit rules and
  objective checks, not every small task. Truly small work stays Direct.

Default to Sol doing useful work, not to a fixed team. Invoke Astra for a concrete
unresolved decision, conflicting evidence, or a consequential independent review;
not for routine sign-off. Use one bounded consultation first, then let the same
owner continue. Choose Luna only when a batch benefits from delegation, not when
one existing command suffices. No required ladder of failed cheaper models.

One controller owns each coordinated run; the Host owns acceptance in Solo.
The Host retains user communication,
permissions, actual workspace safety, integration, and final delivery. Workers
must not create subagents or approve the overall result. Never silently replace a
model, reasoning effort, agent type, or permission boundary.

## Keep work moving

Existing authorization covers ordinary in-scope implementation, local tests,
repairs, and reruns. A plan, test failure, missing optional packet field, or stage
boundary is not a new approval request. Repair recoverable gaps inside the team.
Pause only for new authority, a consequential missing user choice, or a genuine
blocker with no safe in-scope next action. Cite the exact constraint when pausing.

Use one active owner per write scope, not one immutable owner forever. A handoff
requires stopping the old worker **and its mutating processes**, preserving and
inspecting its diff, and assigning the new owner before writing resumes.

Prefer existing code, standard libraries, and platform features before adding
implementation. Preserve requested behavior, correctness, security, accessibility,
and maintainability. Fewer lines are not success if they cut a requirement.
The Ponytail-inspired implementation check lives in the orchestration reference;
it adds no agent, hook, permanent mode, or approval step.

## Evidence and completion

Define the smallest falsifiable check before delegated execution. Review actual
files, diff, outputs, and requirement coverage, not just worker summaries. Reuse
fresh evidence for an unchanged candidate; rerun checks affected by later edits.
Verification is proportional: no full build for a typo, no smoke-only acceptance
for a migration. Never lower a stated passing condition.

Use final verdict `PASS | FIX | BLOCKED`: PASS needs complete evidenced coverage;
FIX means authorized work continues; BLOCKED means no safe next step is available.
Correct a concrete failure with new evidence; do not repeat an unchanged attempt.
After two consecutive no-progress attempts, reassess with the controller and
stop that recovery path. Progress or a safe alternate path may justify continuing
within the original authorization and budget, not an infinite retry loop.

Use a short resume packet only for long or interrupted work. Preserve completed
evidence, ownership, candidate identity, and attempts. Deliver verified completed
parts separately if another part is genuinely blocked.
