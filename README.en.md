[简体中文](README.md) · [English](README.en.md)

> **Sol 6.1 candidate, not released.** This page and its illustrations describe the candidate. Installed-profile loading and cross-platform acceptance are still pending. See the [release preparation record](docs/release/sol61-readiness.md).

![Codex PROVE: Sol does the main work, Astra tackles hard questions, Luna handles batches](docs/assets/readme/hero-en.svg)

<p align="center">
  <a href="https://github.com/yehyakin/codex-prove/releases"><img alt="Release" src="https://img.shields.io/github/v/release/yehyakin/codex-prove?style=flat-square"></a>
  <a href="https://github.com/yehyakin/codex-prove/actions/workflows/posix-validation.yml"><img alt="Linux / macOS CI" src="https://img.shields.io/github/actions/workflow/status/yehyakin/codex-prove/posix-validation.yml?branch=main&amp;label=Linux%20%2F%20macOS&amp;style=flat-square"></a>
  <a href="https://github.com/yehyakin/codex-prove/actions/workflows/windows-validation.yml"><img alt="Windows CI" src="https://img.shields.io/github/actions/workflow/status/yehyakin/codex-prove/windows-validation.yml?branch=main&amp;label=Windows&amp;style=flat-square"></a>
  <a href="LICENSE"><img alt="Apache-2.0 License" src="https://img.shields.io/github/license/yehyakin/codex-prove?style=flat-square"></a>
</p>

# Codex PROVE

**Let Sol finish the task. Bring in help when it helps.**

PROVE is a model-routing skill for Codex. **Sol 6.1 does the main work, Astra tackles hard questions, and Luna handles batches.** Keep a cohesive task in one context; split it only when separate work can make useful progress.

A copy change or small fix stays with your current Codex. A feature can span several files without needing a planning agent followed by an implementation agent. Describe the goal and boundaries; PROVE decides whether help is useful and checks the real result.

[Routing](#how-work-is-routed) · [Install](#install) · [Usage](#usage) · [What's new](#whats-new)

## How work is routed

Start with the simplest useful route. No task has to use every model.

| Task | Route |
| --- | --- |
| Small edit or clear question (Direct) | Your current Codex completes it, with zero agents |
| One cohesive feature or investigation (Solo) | Sol plans, implements, and checks it; no separate planner |
| Analysis or review only (Assist) | Sol analyzes; Astra handles a specific hard question or independent risk review; no implementation |
| Multiple independent workstreams (Coordinated) | Sol coordinates parallel work with explicit file ownership |

| Model | What it does | Default effort |
| --- | --- | --- |
| GPT-6.1 Sol | Complete tasks, routine development, and useful coordination and acceptance | high |
| GPT-6 Astra | One hard question or independent risk review; read-only | high |
| GPT-6 Luna | Mechanical batches with explicit rules and objective checks | max |

If your current Codex is already Sol 6.1, reuse it and its verified effort setting. A self-contained mechanical batch can go straight to Luna. Astra is not a mandatory approval stage.

Less context transfer and fewer unnecessary agents are design goals, not measured savings. **There is no same-task cost or speed A/B result for this candidate.** Count planning, review, and rework in real costs. The [cost notes](docs/costs.md#english) retain historical budgets, not results for this version.

## Install

You need Git, Python 3.11+, and Codex with custom-agent support. The defaults use the three models above; a task needs only the models it actually invokes. Check account availability and supported effort settings before installation.

### macOS / Linux

```sh
git clone https://github.com/yehyakin/codex-prove.git
cd codex-prove
bash scripts/validate.sh
bash scripts/install.sh
```

### Windows

Windows PowerShell 5.1:

```powershell
git clone https://github.com/yehyakin/codex-prove.git
Set-Location codex-prove
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
```

For PowerShell 7, run these from the repository directory:

```powershell
pwsh -NoProfile -File scripts/validate.ps1
pwsh -NoProfile -File scripts/install.ps1
```

The installer backs up the previous version, leaves your existing `~/.codex/config.toml` alone, and doesn't touch unrelated agents. Open a new Codex session when it's done.

These commands fetch `main`, not this candidate branch. The published [v1.1.0](https://github.com/yehyakin/codex-prove/releases/tag/v1.1.0) uses the old routing; its runtime records do not validate the candidate. Candidate installation is for explicitly authorized release checks, not routine upgrades.

## Usage

Put `$codex-prove` before your task, then describe what you want as usual:

```text
$codex-prove Add an account settings page where users can change their name and avatar.
Use the existing login API and UI components. Leave payments alone and run the tests when done.
```

No form to fill out. No agent count to choose. Say what you want and what should stay untouched.

![Small tasks stay direct; Sol completes cohesive work; independent work can be split when useful](docs/assets/readme/control-plane-en.svg)

For that settings page, one Sol would normally inspect the API, edit the page, and run tests. Split off a module only when it can progress independently. Consult Astra about a concrete unresolved problem; use Luna when there is enough repetitive work to justify delegation.

Each write scope has one active owner. Before a handoff, stop the old agent and its mutating processes, then inspect and preserve its changes. Check real files, tests, and requirement coverage before delivery. These are workflow rules, not file locks or enforced isolation.

If you only want to discuss a plan, say so:

```text
$codex-prove Look at this project's login setup and compare ways to improve it. Don't change any code yet.
```

**PROVE only runs when you ask for `$codex-prove`.** Use Codex normally the rest of the time. Even when you invoke PROVE, small tasks stay direct, without extra agents. It responds in Simplified Chinese by default; ask for English or another language if you prefer.

## What's new

This candidate reduces context handoffs and unnecessary role changes.

- **Sol first.** Sol 6.1 takes routine execution and coordination; Terra leaves the defaults. The four stable role IDs remain, without requiring a four-agent team.
- **Keep cohesive work together.** Solo plans, implements, and checks its own task. Parallelize useful independent work only.
- **Consult Astra about a problem.** Use it for hard questions or necessary independent reviews, not routine sign-off.
- **Less setup chatter.** When the launch record identifies the model, work can start without a separate round of agents introducing themselves.
- **Keep moving when it's safe.** Local edits and tests you've already authorized don't stop for approval just because a test fails or a heading is missing. New permissions and important unresolved choices still need your input.
- **Less unnecessary code.** Borrowing from Ponytail, check what the project and standard library already offer before adding dependencies or abstractions.

These changes are not released yet. See the [release preparation record](docs/release/sol61-readiness.md) and [peer research](docs/research/2026-09-30-peer-release-readiness.md) for evidence and gaps. The [v1.1.0 release notes](docs/release/v1.1.0.md) and [historical compatibility matrix](docs/release/runtime-surface-matrix.md) retain their original scope; they do not automatically cover this version.

## A few common questions

**Are more agents always faster?**

No. Independent tasks can run in parallel, but splitting work, passing context, and waiting for results take time too. PROVE only launches agents when they help, within your Codex session's thread limit.

**Where did Terra go?**

Terra is no longer the default execution model. The `prove-complex-worker` role ID stays, now selecting Sol 6.1. Role names do not bind the project to a model. An explicitly requested model is never silently replaced.

**Can I change the models?**

Yes. The profiles are in [`.codex/agents/`](.codex/agents/prove-controller.toml). Sol and Astra default to `high`; Luna uses `max`. Validation checks TOML, model identifier syntax, and effort values without locking models to the defaults. It cannot prove account availability. Check that first, then validate, reinstall, and inspect the actual role mapping in a new session. See the [model configuration notes](.agents/skills/codex-prove/references/runtime-notes.md).

**Does the old Sol Control command still work?**

Yes, `$sol-control` remains an explicit compatibility alias. The project is now called Codex PROVE, so a model upgrade doesn't need another rename. [Rename notes](CODEX_PROVE_V1_IMPLEMENTATION_REPORT.md)

**Installed, but the skill is missing or a model won't launch?**

Start a new session, check that installation succeeded, and make sure the model is available in your Codex. Pulling source alone doesn't update the installed copy, and existing sessions don't reload profiles automatically. If it's still broken, open an [issue](https://github.com/yehyakin/codex-prove/issues/new/choose) with your OS, Codex version, and the error, with private information removed.

## Update or uninstall

Run `git status --short` first and keep any changes you've made. Once the working tree is clean:

```sh
git switch main
git pull --ff-only origin main
```

Run the validation and installation commands for your OS again, then open a new session. The installer prints the backup location. If it finds manually changed local files, it stops instead of overwriting them.

<details>
<summary>Uninstall, or restore the last backup</summary>

macOS / Linux:

```sh
bash scripts/uninstall.sh
# To restore the last backup instead:
bash scripts/uninstall.sh --restore-latest
```

Windows PowerShell 5.1:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1
# Restore the last backup:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1 -RestoreLatest
```

PowerShell 7:

```powershell
pwsh -NoProfile -File scripts/uninstall.ps1
# Restore the last backup:
pwsh -NoProfile -File scripts/uninstall.ps1 -RestoreLatest
```

Only files installed by this project are removed. Other skills and agents stay in place.

</details>

## Feedback and contributions

Maintained by [@yehyakin](https://github.com/yehyakin). We support macOS, Linux, and Windows, covering current `main` and the latest release; see [SUPPORT.md](SUPPORT.md) for details. This is a community project, not an official OpenAI product.

Issues, PRs, and honest feedback are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing. To see how it works internally, start with the [skill](.agents/skills/codex-prove/SKILL.md) and [scheduling notes](.agents/skills/codex-prove/references/orchestration.md).

For security issues, follow [SECURITY.md](SECURITY.md) and use [private vulnerability reporting](https://github.com/yehyakin/codex-prove/security/advisories/new). Keep tokens, private configuration, and private project code out of public issues.

## Inspiration and license

This project draws on [Ponytail](https://github.com/DietrichGebert/ponytail) for keeping implementations small, [Superpowers](https://github.com/obra/superpowers) for task splitting and review, and other community orchestration projects. Specific sources and attribution are in the [research notes](docs/research/2026-09-25-peer-orchestration.md) and [NOTICE](NOTICE).

Licensed under [Apache License 2.0](LICENSE).

**致谢 / Thanks**

Thank you to the [LINUX DO forum](https://linux.do/) community for its attention, feedback, and support.
