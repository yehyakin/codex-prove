#!/usr/bin/env python3
"""Opt-in, bounded POSIX CLI probe in a disposable workspace; not a benchmark.

Codex may persist a project-trust entry even with --ignore-user-config. The caller
must compare its config baseline and clean only the probe-owned entry afterward;
this harness never restores an entire shared config file automatically.
CLI usage is root-only. Retaining a transcript does not discover descendants or
make this a whole-run collector; missing/failed usage remains unknown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from worker_model_pilot import parse_usage, run_process, save, snapshot


ROOT = Path(__file__).resolve().parents[1]


def task_snapshot(workspace):
    return {path: value for path, value in snapshot(workspace).items()
            if path != ".git" and not path.startswith(".git/")}


def prepare_prompt(task_prompt, model, effort):
    """Expose this launcher's selection, not a claim about effective execution."""
    selection = {
        "source": "this invocation's explicit CLI arguments",
        "scope": "current_host_only",
        "selected_model": model,
        "selected_reasoning_effort": effort,
        "observed_model": None,
        "observed_reasoning_effort": None,
    }
    prompt = (
        "Launcher context for this Host only (not child identity or a provider receipt). "
        "Selected settings may be overridden by managed policy or the runtime; "
        "observed settings remain unknown. This does not change task scope, "
        "permissions, or prescribe a route.\n"
        + json.dumps(selection, ensure_ascii=False, sort_keys=True)
        + "\n\n" + task_prompt
    )
    return selection, prompt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-model", action="store_true", help="Explicitly allow one account-usage call and requested subagents")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--sandbox", choices=("read-only", "workspace-write"), default="workspace-write")
    parser.add_argument("--max-agent-threads", type=int, default=2,
                        help="Invocation-local open-agent limit (1..8); completed agents may retain slots")
    parser.add_argument("--retain-session", action="store_true",
                        help="Keep Codex's local session transcript for launch-evidence inspection")
    args = parser.parse_args()
    workspace, output = args.workspace.resolve(), args.output.resolve()
    if not args.run_model:
        parser.error("model calls require --run-model")
    if not args.codex or not 1 <= args.timeout <= 600:
        parser.error("Codex and a timeout of 1..600 seconds are required")
    if not 1 <= args.max_agent_threads <= 8:
        parser.error("max-agent-threads must be 1..8")
    if workspace == ROOT or ROOT in workspace.parents or not (workspace / ".git").is_dir():
        parser.error("use a disposable Git workspace outside the source repository")
    if output == ROOT or ROOT in output.parents or output.exists() or output == workspace or workspace in output.parents:
        parser.error("use a new output directory outside the source repository and probe workspace")
    if sys.platform == "win32":
        parser.error("live probes require POSIX process-group cleanup; Windows is not supported")
    task_prompt = args.prompt_file.read_bytes().decode("utf-8")
    selection, launch_prompt = prepare_prompt(task_prompt, "gpt-6.1-sol", "high")
    version = subprocess.run([args.codex, "--version"], check=True, capture_output=True, text=True).stdout.strip()
    output.mkdir(parents=True)
    before = task_snapshot(workspace)
    # These overrides are invocation-local; Codex itself may persist project trust.
    # Never copy credentials, weaken the sandbox, or silently change models/retry.
    command = [args.codex, "exec", "--ignore-user-config",
               *([] if args.retain_session else ["--ephemeral"]),
               "--sandbox", args.sandbox, "-c", 'approval_policy="never"',
               "--model", selection["selected_model"], "-c",
               'model_reasoning_effort=' + json.dumps(selection["selected_reasoning_effort"]),
               "-c", f"agents.max_concurrent_threads_per_session={args.max_agent_threads}",
               "-c", "sandbox_workspace_write.network_access=false",
               "--color", "never", "--json", "-C", str(workspace),
               "--output-last-message", str(output / "final.txt"), "-"]
    save(output / "invocation.json", {
        "command": command, "codex_version": version,
        "prompt_sha256": hashlib.sha256(launch_prompt.encode()).hexdigest(),
        "task_prompt_sha256": hashlib.sha256(task_prompt.encode()).hexdigest(),
        "host_selection": selection,
        "initial_files": before,
        "evidence_scope": "selected CLI settings and actual tool/file behavior; no cost or general quality claim",
    })
    shutil.copyfile(args.prompt_file, output / "task-prompt.txt")
    (output / "prompt.txt").write_bytes(launch_prompt.encode("utf-8"))
    result = run_process(command, workspace, launch_prompt, args.timeout,
                         output / "events.jsonl", output / "runtime.stderr")
    after = task_snapshot(workspace)
    result.update(parse_usage(output / "events.jsonl",
                              process_complete=result["exit_code"] == 0 and not result["timed_out"]))
    result["final_files"] = after
    result["net_changes"] = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    save(output / "result.json", result)
    print(json.dumps({key: result[key] for key in ("exit_code", "timed_out", "elapsed_seconds", "net_changes")}, ensure_ascii=False))
    raise SystemExit(0 if result["exit_code"] == 0 and not result["timed_out"] else 1)


if __name__ == "__main__":
    main()
