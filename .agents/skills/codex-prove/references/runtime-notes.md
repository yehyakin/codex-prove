# Runtime selection and recovery

Read only for agent launch or a runtime problem. Direct work needs no agent proof.
The Host owns authority; runtime capability is not permission.

The source profiles are `.codex/agents/prove-controller.toml`,
`prove-specialist-worker.toml`, `prove-complex-worker.toml`, and
`prove-efficient-worker.toml`. Update the
selected model in these profiles, not the brand, invocation, or role names.
In this Sol 6.1 candidate, `prove-controller` and `prove-complex-worker` select
`gpt-6.1-sol` / `high`. `prove-specialist-worker` selects `gpt-6-astra` / `high`
with read-only scope; `prove-efficient-worker` remains `gpt-6-luna` / `max`.
These are intentional profile migrations, not fallback aliases. Terra leaves
the default routing; do not silently remap an old Terra task or exact-model request.

## Select and record, do not ask for self-attestation

Use the configured role, model, and reasoning effort. Launch in a fresh context
with `fork_turns="none"` and the task-local packet. Check the authoritative
Host/tool role mapping together with the actual launch record once per launch.
A TOML file or a friendly agent name alone does not prove the selected model.

The complete task may be sent on the first turn. No identity-only handshake,
mandatory idle turn, or child self-report of hidden model metadata is required.
If the runtime does not expose a model field to the child, that absence is not
a blocker when the Host's authoritative selection is available.

A current Sol 6.1 Host may plan and implement Solo work or act as controller.
Reuse its authoritatively known, supported user-selected effort; the child profile's
`high` default is not a reason to reset the Host or spawn a duplicate controller.
Record the actual Host settings, not an exact-profile launch if they differ.
An explicit requested model/effort still takes precedence. A Host that implements
does not become an independent reviewer of its own work.

On a different Host, Solo normally means one `prove-complex-worker` owns the whole
bounded task and the Host accepts it; a mechanical batch may go to Luna alone.
Assist uses a read-only Sol or a problem-specific Astra. Only Coordinated may
need a separate controller plus workers. A worker never gains
subagent permission just because its model is also used for the controller.

If custom-agent selection is unavailable or its mapping is stale but the runtime
supports explicit model and effort selection, use a fresh generic agent with
those exact settings and the same profile instructions and task boundary.
Record this as an explicit-profile launch, not a successfully selected custom
agent. Do not assume its sandbox matches the profile.

## Native Nested / Compatibility

Use **Native Nested** (Host → controller → workers) only when custom or explicit
model selection is supported, nesting depth permits it, capacity is available,
and a real launch has demonstrated it. Configuration intent alone is not proof.
The controller must pass along the same task, ownership, and permission bounds.

Otherwise use **Compatibility**: the controller returns the graph, the Host
launches workers, and the controller reviews their real artifacts. Missing
nesting depth does not block this mode. Both modes use the same evidence gate.

Respect the runtime's live capacity; configured maxima are ceilings, not free
slots. Unknown capacity means launch conservatively and queue, not invent a
thread count or repeatedly ask the user. Workers do not create subagents.

## Capability and authorization

The separate controller and Astra specialist profiles request read-only sandboxes;
Sol and Luna execution profiles request workspace-write. Actual permissions depend
on the Host: live parent overrides may take precedence, including in the CLI.
Record any broader capability and keep work inside its authorized operational
scope without calling that scope enforced isolation.

For reversible local work, inspect actual paths and diffs and preserve user edits.
Do not claim net-change snapshots prove zero writes or process quiescence.
When an enforceable boundary is necessary for destructive, production, credential,
privacy-sensitive, or irreversible work, do not launch with a weaker boundary.
A worker cannot acquire permission the Host lacks. Never route around a denied
action through another agent, tool, or purported fallback.

## Fail Closed on false identity, not on missing paperwork

Never silently substitute the model, reasoning effort, type, or permission scope.
If authoritative selection is missing or contradictory, do not claim exact-profile
execution or launch under an unproved identity. Correct the selection or explain
the real capability gap. If the user requires that exact model or an independent
review, keep that requirement blocked until it can be met.

Where the task permits it, disclose a Direct/Host continuation instead of claiming
the unavailable profile ran. Such a change cannot satisfy an explicit exact-model
requirement or widen authorization. A model error, quota limit, or capacity queue
is not permission for a hidden fallback or unlimited paid retries.

Check only profiles needed by the task; lack of Astra or Luna need not block a
Sol-only task. Sol 6.1 not being available means its launch remains unavailable,
not that a similarly named older Sol passed. Local TOML parsing and a simulated
route are not live-model validation. Do not edit global model/provider settings
to force availability. For API-based runtimes, Sol 6.1 tool calling requires
Responses support; a text-only model listing is insufficient.

Repair non-security omissions from existing evidence without repeated user
approval. BLOCKED is reserved for absent required capability, irreconcilable
ownership, missing authority, or no safe remaining action. Preserve verified
partial results and identify exactly what remains unavailable.

## Lifecycle

A timeout is an observation, not proof a worker or command stopped. Inspect
lifecycle and mutating processes before replacement, ownership handoff, or reusing
that scope. Do not launch a racing writer. Capture usable artifacts, repair the
packet, and follow the progress-based recovery limit in the orchestration protocol.

An exhausted work budget stops new attempts, not authorized cancellation of this
task's still-running work. Use runtime cancellation for identified task workers
and commands when permitted; never stop unrelated processes. If termination
cannot be confirmed, keep the affected scope held and report that uncertainty.

Release idle agents when the runtime exposes that capability. Otherwise mark them
idle, reuse compatible contexts for follow-ups, and account for occupied slots.
No new task/thread, permanent hook, or background job is needed for ordinary
orchestration. Keep a resume packet only when interruption or duration warrants it.
