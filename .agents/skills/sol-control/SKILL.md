---
name: sol-control
description: Use only when the user explicitly invokes the legacy $sol-control command; redirect to $codex-prove without activating the old model-specific workflow.
---

# Sol Control compatibility entry

This explicit-only alias follows the installed canonical Skill at
`../codex-prove/SKILL.md`. Treat the invocation as `$codex-prove`, including its
Direct path, current profiles, ownership, runtime selection, and evidence rules.
Read only the references needed for the chosen route; do not recreate the legacy
workflow. If the canonical Skill is missing, report that installation problem
without pretending the alias can provide it.

Tell the user once that `$sol-control` is deprecated in favor of `$codex-prove`.
The alias is retained from v1.0 for migration; it does not pin the old model.
