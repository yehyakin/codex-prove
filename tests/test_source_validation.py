#!/usr/bin/env python3
"""Exercise source selection and configurable profiles without a real install."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path(".codex/agents/prove-complex-worker.toml")


class SourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="prove-source-check.")
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / "source"
        # Mirror tracked and non-ignored source, including documentation media.
        # A recursive "media" exclusion drops linked source files; copying local
        # render outputs and node_modules is also unnecessary for these fixtures.
        files = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT, check=True, capture_output=True,
        ).stdout.decode("utf-8").split("\0")
        for relative in files:
            if not relative or Path(relative).parts[0] == "media":
                continue  # Keep the existing exclusion of root-level scratch art.
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target, follow_symlinks=False)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)

    def run_check(self):
        return subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/validate_source.py"), str(self.root)],
            cwd=self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        )

    def assert_rejected(self, relative: str, reason: str):
        result = self.run_check()
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn(relative, result.stdout.replace("\\", "/"))
        self.assertIn(reason, result.stdout)
        self.assertNotIn("Traceback", result.stdout)
        return result

    def test_clean_source_and_ignored_dependencies(self):
        clean = self.run_check()
        self.assertEqual(0, clean.returncode, clean.stdout)
        (self.root / ".gitignore").write_text("node_modules/\ngenerated/\n", encoding="utf-8")
        dependency = self.root / "node_modules/vendor"
        dependency.mkdir(parents=True)
        (dependency / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        generated = self.root / "generated"
        generated.mkdir()
        (generated / "capture.txt").write_text("generated output without newline ", encoding="utf-8")
        result = self.run_check()
        self.assertEqual(0, result.returncode, result.stdout)

    def test_tracked_ignored_file_is_still_checked(self):
        (self.root / ".gitignore").write_text("generated/\n", encoding="utf-8")
        path = self.root / "generated/tracked.md"
        path.parent.mkdir()
        path.write_text("[bad](absent.md)\n", encoding="utf-8")
        subprocess.run(["git", "add", "-f", "generated/tracked.md"], cwd=self.root, check=True, capture_output=True)
        self.assert_rejected("generated/tracked.md", "link target is missing")

    def test_untracked_source_is_checked_with_private_diagnostics(self):
        path = self.root / "untracked.md"
        path.write_text("[bad](not-here.md)\n", encoding="utf-8")
        self.assert_rejected("untracked.md", "link target is missing")
        token = "sk-" + "a" * 24
        path.write_text(token + "\n", encoding="utf-8")
        result = self.assert_rejected("untracked.md", "possible credential detected")
        self.assertNotIn(token, result.stdout)

    def test_escaping_link_and_whitespace_have_path_diagnostics(self):
        path = self.root / "new.md"
        for text, reason in (
            ("[outside](../outside.md)\n", "escapes repository"),
            ("missing newline", "missing final newline"),
            ("trailing space \n", "trailing whitespace"),
        ):
            with self.subTest(reason=reason):
                path.write_text(text, encoding="utf-8")
                self.assert_rejected("new.md", reason)

    def test_custom_model_and_effort_can_pass_install_check(self):
        path = self.root / PROFILE
        source = path.read_text(encoding="utf-8")
        source = source.replace('model = "gpt-6.1-sol"', 'model = "gpt-6-sol"')
        source = source.replace('model_reasoning_effort = "high"', 'model_reasoning_effort = "medium"')
        path.write_text(source, encoding="utf-8")
        result = self.run_check()
        self.assertEqual(0, result.returncode, result.stdout)
        if os.name == "nt":
            shell = shutil.which("pwsh") or shutil.which("powershell")
            self.assertIsNotNone(shell, "Windows installation check requires PowerShell")
            command = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/install.ps1", "-Check"]
        else:
            command = ["bash", "scripts/install.sh", "--check"]
        destination = self.parent / "not-created-home"
        env = os.environ.copy()
        env["ORCHESTRATE_HOME"] = str(destination)
        env.pop("ORCHESTRATE_FAILPOINT", None)
        result = subprocess.run(command, cwd=self.root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertFalse(destination.exists(), "check mode wrote an installation")

    def test_invalid_profiles_fail_without_weakening_role_safety(self):
        path = self.root / PROFILE
        original = path.read_text(encoding="utf-8")
        for old, new, reason in (
            ('model = "gpt-6.1-sol"', 'model = ""', "model must"),
            ('model = "gpt-6.1-sol"', 'model = "gpt broken"', "model must"),
            ('model_reasoning_effort = "high"', 'model_reasoning_effort = "invalid"', "reasoning effort"),
            ('model_reasoning_effort = "high"', 'model_reasoning_effort = []', "reasoning effort"),
            ('sandbox_mode = "workspace-write"', 'sandbox_mode = "danger-full-access"', "invalid sandbox_mode"),
            ('model = "gpt-6.1-sol"', 'model = "gpt-6.1-sol"\nmodel = "other"', "invalid TOML"),
        ):
            with self.subTest(reason=reason, replacement=new):
                path.write_text(original.replace(old, new), encoding="utf-8")
                self.assert_rejected(PROFILE.as_posix(), reason)

    def test_both_entrypoints_use_shared_source_checks(self):
        for script in ("validate.sh", "validate.ps1"):
            text = (self.root / "scripts" / script).read_text(encoding="utf-8")
            self.assertIn("validate_source.py", text)
            self.assertNotIn("expected_agents", text)
            self.assertNotIn("agentExpectations", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
