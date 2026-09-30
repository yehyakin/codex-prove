#!/usr/bin/env python3
"""Shared offline source checks for POSIX and Windows installers (Python 3.11+)."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

root = Path(sys.argv[1]).resolve()


def stop(message: str = "source contract mismatch") -> "NoReturn":
    print(f"Validation: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        stop(f"{path.relative_to(root)}: cannot read UTF-8 text")


def frontmatter(path: Path) -> dict[str, str]:
    lines = text(path).splitlines()
    if not lines or lines[0] != "---":
        stop()
    try:
        close = lines[1:].index("---") + 1
    except ValueError:
        stop()
    values: dict[str, str] = {}
    for line in lines[1:close]:
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.+)", line)
        if not match:
            stop()
        values[match.group(1)] = match.group(2).strip().strip('"')
    if set(values) != {"name", "description"}:
        stop()
    return values


canonical = root / ".agents/skills/codex-prove"
skill_path = canonical / "SKILL.md"
skill_meta = frontmatter(skill_path)
if skill_meta["name"] != "codex-prove" or "$codex-prove" not in skill_meta["description"]:
    stop()
if not skill_meta["description"].startswith("Use only when"):
    stop()

compat = root / ".agents/skills/sol-control"
compat_meta = frontmatter(compat / "SKILL.md")
if compat_meta["name"] != "sol-control" or "$sol-control" not in compat_meta["description"]:
    stop()

skill_text = text(skill_path)
contract_text = text(canonical / "references/orchestration.md")
runtime_text = text(canonical / "references/runtime-notes.md")
combined = "\n".join((skill_text, contract_text, runtime_text))
for marker in (
    "Planning", "Routing", "Ownership", "Verification", "Evidence",
    "ordinary small work stays", "explicit", "Requirement ID", "write_scope",
    "one owner", "live capacity", "Native Nested", "Compatibility",
    "fork_turns=\"none\"", "Fail Closed", "PASS | FIX | BLOCKED",
    "verify the verifier", "result-only", "resume packet",
    "prove-controller", "prove-complex-worker", "prove-efficient-worker",
    "prove-specialist-worker",
):
    if marker.lower() not in combined.lower():
        stop()

openai_text = text(canonical / "agents/openai.yaml")
if "$codex-prove" not in openai_text or not re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", openai_text):
    stop()
compat_text = text(compat / "SKILL.md") + "\n" + text(compat / "agents/openai.yaml")
if "$sol-control" not in compat_text or "$codex-prove" not in compat_text:
    stop()
if not re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", compat_text):
    stop()

# Model/effort are user configuration. Release defaults belong in regression
# tests; installation validates syntax and the role's safety contract only.
expected_agents = {
    "prove-specialist-worker.toml": ("prove-specialist-worker", "read-only"),
    "prove-controller.toml": ("prove-controller", "read-only"),
    "prove-complex-worker.toml": ("prove-complex-worker", "workspace-write"),
    "prove-efficient-worker.toml": ("prove-efficient-worker", "workspace-write"),
}
efforts = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
for filename, (name, sandbox) in expected_agents.items():
    path = root / ".codex/agents" / filename
    relative = path.relative_to(root)
    try:
        data = tomllib.loads(text(path))
    except tomllib.TOMLDecodeError:
        stop(f"{relative}: invalid TOML")
    for key, expected in (("name", name), ("sandbox_mode", sandbox)):
        if data.get(key) != expected:
            stop(f"{relative}: invalid {key}")
    model = data.get("model")
    if not isinstance(model, str) or not re.fullmatch(r"[^\s\x00-\x1f\x7f]+", model):
        stop(f"{relative}: model must be a non-empty identifier without whitespace")
    effort = data.get("model_reasoning_effort")
    if not isinstance(effort, str) or effort not in efforts:
        stop(f"{relative}: unsupported reasoning effort value")
    for key in ("description", "developer_instructions"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            stop(f"{relative}: missing {key}")
    if filename != "prove-controller.toml" and not re.search(
        r"do not .*?(?:spawn|create).*?subagent", data["developer_instructions"], re.I | re.S
    ):
        stop(f"{relative}: worker delegation boundary is missing")

for forbidden in ("IPZOR", "Buzz", "DeepSeek", "OpenPencil"):
    for path in (canonical, compat):
        for candidate in path.rglob("*"):
            if candidate.is_file() and re.search(forbidden, text(candidate), re.I):
                stop()

# Include tracked files even if ignored, plus all unignored new candidate files.
# Do not recurse into generated dependencies or dereference source symlinks.
try:
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
except OSError:
    stop("Git is required to enumerate repository sources")
if listing.returncode:
    stop("cannot enumerate repository sources with Git")
source_paths = sorted({
    root / os.fsdecode(item) for item in listing.stdout.split(b"\0") if item
})
source_paths = [path for path in source_paths if path.is_file() and not path.is_symlink()]

for markdown in source_paths:
    if markdown.suffix.lower() != ".md":
        continue
    source = re.sub(
        r"(?ms)^(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?P=fence)[ \t]*$",
        "",
        text(markdown),
    )
    for match in re.finditer(r"\]\(\s*(<[^>]+>|[^)\s]+)", source):
        target = match.group(1)
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            continue
        candidate = (markdown.parent / target).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            stop(f"{markdown.relative_to(root)}: local link escapes repository")
        if not candidate.exists():
            stop(f"{markdown.relative_to(root)}: local link target is missing")

credential_patterns = (
    re.compile("AKIA" + r"[0-9A-Z]{16}"),
    re.compile("-" * 5 + r"BEGIN [A-Z0-9 ]+ PRIVATE KEY" + "-" * 5),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_./+=-]{16,}['\"]"),
)
for path in source_paths:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    if source and not source.endswith("\n"):
        stop(f"{path.relative_to(root)}: missing final newline")
    if any(line.endswith((" ", "\t")) for line in source.splitlines()):
        stop(f"{path.relative_to(root)}: trailing whitespace")
    if any(pattern.search(source) for pattern in credential_patterns):
        stop(f"{path.relative_to(root)}: possible credential detected (value withheld)")

active_public_files = (
    root / "README.md", root / "README.en.md", root / "SECURITY.md",
    root / "CONTRIBUTING.md", root / "SUPPORT.md",
    root / ".github/ISSUE_TEMPLATE/config.yml",
)
for path in active_public_files:
    source = text(path)
    if "github.com/yehyakin/codex-sol-control" in source:
        stop()

for script_name in ("install.ps1", "validate.ps1", "uninstall.ps1"):
    source = text(root / "scripts" / script_name).lower()
    for marker in ("codex-prove", "prove-controller.toml", "prove-complex-worker.toml", "prove-efficient-worker.toml", "prove-specialist-worker.toml"):
        if marker not in source:
            stop()

workflow = text(root / ".github/workflows/windows-validation.yml").lower()
for marker in ("windows-latest", "windows-2022", "powershell", "pwsh", "windows-lifecycle.ps1", "unittest discover"):
    if marker not in workflow:
        stop()
