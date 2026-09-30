#!/usr/bin/env python3
"""Opt-in, bounded POSIX CLI probe in a disposable workspace; not a benchmark."""

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-model", action="store_true", help="Explicitly allow one account-usage call and requested subagents")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--sandbox", choices=("read-only", "workspace-write"), default="workspace-write")
    args = parser.parse_args()
    workspace, output = args.workspace.resolve(), args.output.resolve()
    if not args.run_model:
        parser.error("model calls require --run-model")
    if not args.codex or not 1 <= args.timeout <= 600:
        parser.error("Codex and a timeout of 1..600 seconds are required")
    if workspace == ROOT or ROOT in workspace.parents or not (workspace / ".git").is_dir():
        parser.error("use a disposable Git workspace outside the source repository")
    if output == ROOT or ROOT in output.parents or output.exists() or output == workspace or workspace in output.parents:
        parser.error("use a new output directory outside the source repository and probe workspace")
    if sys.platform == "win32":
        parser.error("live probes require POSIX process-group cleanup; Windows is not supported")
    task_prompt = args.prompt_file.read_text(encoding="utf-8")
    version = subprocess.run([args.codex, "--version"], check=True, capture_output=True, text=True).stdout.strip()
    output.mkdir(parents=True)
    before = task_snapshot(workspace)
    # Overrides are invocation-local. Never edit user config, copy credentials,
    # weaken the sandbox, or silently change models/retry a failed probe.
    command = [args.codex, "exec", "--ignore-user-config", "--ephemeral",
               "--sandbox", args.sandbox, "-c", 'approval_policy="never"',
               "--model", "gpt-6.1-sol", "-c", 'model_reasoning_effort="high"',
               "-c", "agents.max_concurrent_threads_per_session=2",
               "-c", "sandbox_workspace_write.network_access=false",
               "--color", "never", "--json", "-C", str(workspace),
               "--output-last-message", str(output / "final.txt"), "-"]
    save(output / "invocation.json", {
        "command": command, "codex_version": version,
        "prompt_sha256": hashlib.sha256(task_prompt.encode()).hexdigest(),
        "initial_files": before,
        "evidence_scope": "selected CLI settings and actual tool/file behavior; no cost or general quality claim",
    })
    shutil.copyfile(args.prompt_file, output / "prompt.txt")
    result = run_process(command, workspace, task_prompt, args.timeout,
                         output / "events.jsonl", output / "runtime.stderr")
    after = task_snapshot(workspace)
    result.update(parse_usage(output / "events.jsonl"))
    result["final_files"] = after
    result["net_changes"] = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    save(output / "result.json", result)
    print(json.dumps({key: result[key] for key in ("exit_code", "timed_out", "elapsed_seconds", "net_changes")}, ensure_ascii=False))
    raise SystemExit(0 if result["exit_code"] == 0 and not result["timed_out"] else 1)


if __name__ == "__main__":
    main()
