#!/usr/bin/env python3
"""Development-only matched worker pilot, not a Skill runtime or full A/B suite.

Defaults to free oracle calibration. --run-models explicitly enables 18 serial
Codex calls. All workspaces/logs stay in a new caller-selected temporary directory.
No model fallback, retry, global install, permission bypass, or cost extrapolation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time
import tomllib
import uuid


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "tests/fixtures/worker_model_cases.py"
PROFILE = ROOT / ".codex/agents/prove-complex-worker.toml"
MODELS = ("gpt-5.6-terra", "gpt-6-sol")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def cases():
    spec = importlib.util.spec_from_file_location("pilot_cases", CASE_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CASES


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def seed(path, files):
    path.mkdir(parents=True, exist_ok=False)
    for name, body in files.items():
        (path / name).write_text(body, encoding="utf-8")


def snapshot(path):
    result = {}
    for item in sorted(path.rglob("*")):
        relative = item.relative_to(path)
        if item.is_symlink():
            result[relative.as_posix()] = "symlink:" + os.readlink(item)
        elif item.is_dir():
            result[relative.as_posix()] = "directory"
        elif item.is_file():
            result[relative.as_posix()] = hashlib.sha256(item.read_bytes()).hexdigest()
    return result


def changed(before, after):
    return sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))


def run_process(command, cwd, input_text, timeout, stdout_path, stderr_path, *, clean_env=False):
    """Bounded POSIX process group; no shell interpolation or approval bypass."""
    env = ({"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
           if clean_env else dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    started = time.monotonic()
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=out,
                                stderr=err, text=True, env=env, start_new_session=True)
        timed_out = False
        try:
            proc.communicate(input_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            # The cell owns this new process group. End lingering tool children
            # before judging, even if the top-level CLI has already returned.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
    return {"exit_code": proc.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3)}


def grade(case, workspace, logs, label="grade", *, live=False, public=False):
    before = snapshot(workspace)
    marker = "PROVE_PILOT_" + uuid.uuid4().hex + ":"
    body = ("import unittest\nsuite = unittest.defaultTestLoader.discover('.')\n" if public
            else case["grader"] + "\nsuite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)\n")
    body += ("\n_prove_check_framework()\n"
             "result = unittest.TextTestRunner(verbosity=2).run(suite)\n"
             "_prove_check_framework()\n"
             "import json\n"
             f"print({marker!r} + json.dumps({{'tests_run': result.testsRun, "
             "'skipped': len(result.skipped), 'success': result.wasSuccessful()}), flush=True)\n"
             "raise SystemExit(0 if result.wasSuccessful() else 1)\n")
    # -I/-S exclude user Python startup code; add only this fixture to imports.
    # Reject persistent replacement of the test machinery by candidate imports
    # or tests. This is a bounded integrity check, not adversarial-code isolation.
    guard = (
        "import unittest\n"
        "_prove_framework = [(owner, name, value, getattr(value, '__code__', None))\n"
        " for owner in (unittest, unittest.TestCase, unittest.TestResult,\n"
        "               unittest.TextTestResult, unittest.TestSuite, unittest.TextTestRunner)\n"
        " for name, value in vars(owner).items() if callable(value)]\n"
        "def _prove_check_framework():\n"
        " for owner, name, value, code in _prove_framework:\n"
        "  if getattr(owner, name, None) is not value or getattr(value, '__code__', None) is not code:\n"
        "   raise RuntimeError('test framework was modified')\n"
    )
    body = "import os, sys\nsys.path.insert(0, os.getcwd())\n" + guard + body
    command = [sys.executable, "-I", "-S", "-B", "-c", body]
    if live:
        if sys.platform != "darwin" or not Path("/usr/bin/sandbox-exec").is_file():
            return {"pass": False, "blocked": "live grading requires the tested macOS sandbox"}
        policy = '(version 1) (allow default) (deny file-write*) (deny network*) (deny file-read* (subpath "/Users"))'
        command = ["/usr/bin/sandbox-exec", "-p", policy, *command]
    result = run_process(command, workspace, None, 15, logs / f"{label}.stdout",
                         logs / f"{label}.stderr", clean_env=True)
    receipts = []
    for line in (logs / f"{label}.stdout").read_text(encoding="utf-8").splitlines():
        if line.startswith(marker):
            try:
                receipts.append(json.loads(line[len(marker):]))
            except json.JSONDecodeError:
                pass
    receipt = receipts[0] if len(receipts) == 1 else {}
    count = receipt.get("tests_run")
    count_ok = type(count) is int and (count >= 1 if public else count == case.get("expected_checks"))
    result["receipt"] = receipt
    result["mutated_candidate"] = snapshot(workspace) != before
    result["pass"] = (result["exit_code"] == 0 and not result["timed_out"]
                      and not result["mutated_candidate"] and count_ok
                      and receipt.get("success") is True and receipt.get("skipped") == 0)
    return result


def calibrate(case, path):
    path.mkdir(parents=True)
    seed(path / "broken", case["files"])
    seed(path / "oracle", case["files"] | case["oracle"])
    broken = grade(case, path / "broken", path, "broken")
    oracle = grade(case, path / "oracle", path, "oracle")
    # A syntax/import failure does not prove the known defect was detected.
    broken_log = (path / "broken.stderr").read_text(encoding="utf-8")
    meaningful_failure = "FAIL:" in broken_log and "Ran " in broken_log
    passed = not broken["pass"] and meaningful_failure and oracle["pass"]
    return {"case_id": case["id"], "pass": passed, "broken": broken, "oracle": oracle}


def prompt(case, instructions):
    return f"""{instructions}

You own one isolated synthetic maintenance fixture, not the PROVE source repository.
Objective: {case['objective']}
Acceptance criteria: {case['requirements'].strip()}
Read scope: files in this working directory only.
Write scope: {', '.join(case['owned'])} only. You may extend the tests there.
Forbidden: other files/directories, network, config/auth files, git operations,
dependencies, background processes, additional agents and delegated work.
Inputs: the existing source, helper and public unit tests in this directory.
Minimum verification: {sys.executable} -B -m unittest discover -v; exit 0.
Add relevant regression checks in the owned test file and run them on the final candidate.
Do not ask for an identity handshake or new approval for in-scope repairs.
Return the actual changes, verification command/result and remaining limitations.
An external acceptance check will run after your process ends; do not search for it.
"""


def parse_usage(path):
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    seen = False
    invalid = False
    failed = False
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") in ("turn.failed", "error"):
            failed = True
        if event.get("type") != "turn.completed":
            continue
        usage = event.get("usage", {})
        seen = True
        if not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0 for k in totals):
            invalid = True
            continue
        if usage["cached_input_tokens"] > usage["input_tokens"]:
            invalid = True
            continue
        for key in totals:
            totals[key] += usage[key]
    return {"usage": totals if seen and not invalid else None,
            "completed_event": seen, "error_event": failed}


def schedule(repetitions=3):
    for repetition in range(1, repetitions + 1):
        for index, case in enumerate(cases()):
            order = MODELS if (index + repetition) % 2 == 0 else MODELS[::-1]
            for model in order:
                yield case, model, repetition


def execute(case, model, repetition, output, codex, timeout, task_prompt):
    cell_id = f"{case['id']}-{model}-r{repetition}"
    cell = output / "cells" / cell_id
    cell.mkdir(parents=True)
    workspace = cell / "workspace"
    seed(workspace, case["files"])
    before = snapshot(workspace)
    command = [codex, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
               "--sandbox", "workspace-write", "-c", 'approval_policy="never"',
               "--model", model, "-c", 'model_reasoning_effort="high"',
               "--color", "never", "--json", "-C", str(workspace),
               "--output-last-message", str(cell / "final.txt"), "-"]
    save(cell / "invocation.json", {"command": command, "prompt_sha256": digest(task_prompt)})
    (cell / "prompt.txt").write_text(task_prompt, encoding="utf-8")
    run = run_process(command, workspace, task_prompt, timeout,
                      cell / "events.jsonl", cell / "runtime.stderr")
    after = snapshot(workspace)
    net_changes = changed(before, after)
    tests_modified = any(path.startswith("test_") for path in net_changes)
    integrity = (all(path in case["owned"] for path in net_changes)
                 and not any(value.startswith("symlink:") for value in after.values()))
    # Never run generated code after an observed scope violation.
    check = grade(case, workspace, cell, live=True) if integrity else {"pass": False, "skipped": "scope violation"}
    public_check = (grade(case, workspace, cell, "public", live=True, public=True)
                    if integrity else {"pass": False, "skipped": "scope violation"})
    telemetry = parse_usage(cell / "events.jsonl")
    row = {"case_id": case["id"], "model_requested": model, "effort_requested": "high",
           "repetition": repetition, "base_sha256": digest(before),
           "prompt_sha256": digest(task_prompt), "grader_sha256": digest(case["grader"]),
           "candidate_identity": digest(after), "changed_files": net_changes,
           "integrity_pass": integrity, "grading": check, "public_tests": public_check,
           "tests_modified": tests_modified, "run": run, **telemetry,
           "cost_value": None, "cost_unit": None, "automatic_retries": 0}
    row["pass"] = (integrity and tests_modified and check["pass"] and public_check["pass"] and run["exit_code"] == 0
                   and not run["timed_out"] and telemetry["completed_event"] and not telemetry["error_event"])
    save(cell / "result.json", row)
    return row


def summarize(rows, expected=18):
    identities, seen = {}, set()
    for row in rows:
        key = (row["case_id"], row["model_requested"], row["repetition"])
        if key in seen:
            raise ValueError("duplicate result cell")
        seen.add(key)
        identity = tuple(row[k] for k in ("base_sha256", "prompt_sha256", "grader_sha256"))
        if row["case_id"] in identities and identities[row["case_id"]] != identity:
            raise ValueError("unmatched base, prompt or grader; cannot compare")
        identities[row["case_id"]] = identity
    by_model = {}
    for model in MODELS:
        group = [r for r in rows if r["model_requested"] == model]
        if not group:
            continue
        usages = [r["usage"] for r in group]
        by_model[model] = {
            "runs": len(group), "passed": sum(r["pass"] for r in group),
            "median_seconds": round(statistics.median(r["run"]["elapsed_seconds"] for r in group), 3),
            "total_seconds": round(sum(r["run"]["elapsed_seconds"] for r in group), 3),
            "usage_total": ({k: sum(u[k] for u in usages) for k in usages[0]}
                            if all(u is not None for u in usages) else None),
        }
    return {"evidence_class": "worker_model_pilot", "expected_cells": expected,
            "completed_cells": len(rows), "complete": len(rows) == expected,
            "models": by_model, "winner": None, "measured_cost": None,
            "limitations": ["synthetic Python fixtures", "small sample", "serial CLI calls, not Desktop roles",
                            "no workflow savings or superiority inference", "CLI selector, not model self-attestation"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New output directory outside the repository")
    parser.add_argument("--run-models", action="store_true", help="Make 18 paid/account-usage model calls")
    parser.add_argument("--codex", default="/Applications/Codex.app/Contents/Resources/codex")
    parser.add_argument("--timeout", type=int, default=180, help="Per cell wall-clock seconds")
    args = parser.parse_args()
    output = args.output.resolve()
    if os.name != "posix":
        parser.error("This development pilot currently requires POSIX process groups")
    if args.run_models and (sys.platform != "darwin" or str(output).startswith("/Users/")):
        parser.error("Live calls currently require macOS and temporary workspaces outside /Users")
    if output == ROOT or ROOT in output.parents or output.exists() or args.timeout <= 0:
        parser.error("Use a new temporary output directory outside the source repository and a positive timeout")
    output.mkdir(parents=True)
    calibration = [calibrate(case, output / "calibration" / case["id"]) for case in cases()]
    save(output / "calibration.json", calibration)
    if not all(item["pass"] for item in calibration):
        print("Calibration failed; no model calls launched.", flush=True)
        return 1
    print("Calibration: all broken baselines rejected; all oracles passed.", flush=True)
    if not args.run_models:
        return 0
    for case in cases():
        location = output / "calibration" / case["id"]
        check = grade(case, location / "oracle", location, "sandbox-preflight", live=True)
        public = grade(case, location / "oracle", location, "public-preflight", live=True, public=True)
        if not check["pass"] or not public["pass"]:
            print("Live sandbox/grade preflight failed; no model calls launched.", flush=True)
            return 1
    version = subprocess.run([args.codex, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    cells = list(schedule())
    profile_bytes = PROFILE.read_bytes()
    instructions = tomllib.loads(profile_bytes.decode("utf-8"))["developer_instructions"]
    prompts = {case["id"]: prompt(case, instructions) for case, _, _ in cells}
    manifest = {"evidence_class": "worker_model_pilot", "codex_version": version,
                "python_version": sys.version.split()[0], "models": MODELS, "effort": "high",
                "repetitions": 3, "timeout_seconds": args.timeout,
                "case_registry_sha256": hashlib.sha256(CASE_FILE.read_bytes()).hexdigest(),
                "profile_sha256": hashlib.sha256(profile_bytes).hexdigest(),
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "cells": [{"case_id": c["id"], "model": m, "repetition": r} for c, m, r in cells]}
    save(output / "manifest.json", manifest)
    rows = []
    for case, model, repetition in cells:
        row = execute(case, model, repetition, output, args.codex, args.timeout, prompts[case["id"]])
        rows.append(row)
        save(output / "results.json", {"manifest_sha256": digest(manifest), "cells": rows})
        save(output / "summary.json", summarize(rows))
        print(f"{len(rows)}/18 {case['id']} {model} r{repetition}: "
              f"{'PASS' if row['pass'] else 'FAIL'} ({row['run']['elapsed_seconds']}s)", flush=True)
        if not row["completed_event"] and not row["run"]["timed_out"]:
            print("Runtime did not complete a turn; stop paid calls and inspect local logs. No fallback.", flush=True)
            return 2
    return 0 if all(row["pass"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
