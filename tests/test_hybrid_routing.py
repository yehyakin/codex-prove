#!/usr/bin/env python3
"""Model-neutral routing and role-profile contracts for Codex PROVE."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-prove"
FORWARD_CASES = ROOT / "tests" / "fixtures" / "forward-cases.json"
CONTROLLER = ROOT / ".codex" / "agents" / "prove-controller.toml"
COMPLEX = ROOT / ".codex" / "agents" / "prove-complex-worker.toml"
EFFICIENT = ROOT / ".codex" / "agents" / "prove-efficient-worker.toml"
SPECIALIST = ROOT / ".codex" / "agents" / "prove-specialist-worker.toml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contract() -> str:
    return "\n".join(
        read(path)
        for path in (
            SKILL / "SKILL.md",
            SKILL / "references" / "orchestration.md",
            SKILL / "references" / "runtime-notes.md",
        )
    )


class AgentProfileTests(unittest.TestCase):
    def test_specialist_profile_uses_sol_high(self) -> None:
        with SPECIALIST.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("prove-specialist-worker", data["name"])
        self.assertEqual("gpt-6-sol", data["model"])
        self.assertEqual("high", data["model_reasoning_effort"])
        self.assertEqual("workspace-write", data["sandbox_mode"])

    def test_controller_profile_is_model_neutral_and_read_only(self) -> None:
        with CONTROLLER.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("prove-controller", data["name"])
        self.assertEqual("gpt-6-astra", data["model"])
        self.assertEqual("high", data["model_reasoning_effort"])
        self.assertEqual("read-only", data["sandbox_mode"])
        self.assertNotIn(data["model"], data["name"])

    def test_complex_profile_uses_current_terra_default(self) -> None:
        with COMPLEX.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("prove-complex-worker", data["name"])
        self.assertEqual("gpt-5.6-terra", data["model"])
        self.assertEqual("high", data["model_reasoning_effort"])
        self.assertEqual("workspace-write", data["sandbox_mode"])

    def test_efficient_profile_uses_current_luna_default(self) -> None:
        with EFFICIENT.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("prove-efficient-worker", data["name"])
        self.assertEqual("gpt-6-luna", data["model"])
        self.assertEqual("max", data["model_reasoning_effort"])
        self.assertEqual("workspace-write", data["sandbox_mode"])

    def test_workers_are_leaf_agents(self) -> None:
        for path in (SPECIALIST, COMPLEX, EFFICIENT):
            with path.open("rb") as handle:
                instructions = tomllib.load(handle)["developer_instructions"].lower()
            self.assertIn("do not", instructions)
            self.assertIn("subagent", instructions)
            self.assertTrue("spawn" in instructions or "create" in instructions)


class ForwardRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(read(FORWARD_CASES))
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_forward_cases_cover_direct_controller_and_three_workers(self) -> None:
        routes = {case["expected"]["route"] for case in self.cases}
        self.assertEqual(
            {"direct", "controller", "controller_then_efficient", "controller_then_complex", "controller_then_specialist", "blocked"},
            routes,
        )

    def test_forward_cases_cover_quiescent_handoff_after_writes(self) -> None:
        allow = self.by_id["efficient-first-failure-before-write-escalates-complex"]
        handoff = self.by_id["efficient-first-failure-after-write-safe-handoff"]
        self.assertEqual("controller_then_complex", allow["expected"]["route"])
        self.assertEqual("controller_then_complex", handoff["expected"]["route"])
        self.assertIn("before", " ".join(allow["required_assertions"]).lower())
        self.assertEqual("quiescent_handoff", handoff["expected"]["ownership"])
        self.assertIn("processes", " ".join(handoff["required_assertions"]).lower())

    def test_forward_cases_cover_one_file_one_owner(self) -> None:
        case = self.by_id["single-file-unique-owner"]
        assertions = " ".join(case["required_assertions"]).lower()
        self.assertIn("owner", assertions)
        self.assertTrue("one" in assertions or "唯一" in assertions)


class PosixRoleLifecycleTests(unittest.TestCase):
    def test_install_and_uninstall_preserve_unrelated_files(self) -> None:
        if os.name == "nt":
            self.skipTest("covered by tests/windows-lifecycle.ps1")
        with tempfile.TemporaryDirectory(prefix="codex-prove-routing-") as raw:
            home = Path(raw)
            config = home / ".codex" / "config.toml"
            other = home / ".codex" / "agents" / "other-agent.toml"
            other.parent.mkdir(parents=True)
            config.write_text("[features.context_management]\nexperimental_mode = true\n", encoding="utf-8")
            other.write_text('name = "other-agent"\n', encoding="utf-8")
            before = (config.read_bytes(), other.read_bytes())
            env = {**os.environ, "ORCHESTRATE_HOME": str(home)}
            install = subprocess.run(
                ["bash", "scripts/install.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertEqual(0, install.returncode, install.stdout)
            profiles = (CONTROLLER, SPECIALIST, COMPLEX, EFFICIENT)
            for source in profiles:
                with self.subTest(profile=source.stem):
                    installed = home / ".codex" / "agents" / source.name
                    self.assertEqual(source.read_bytes(), installed.read_bytes())
            relative_license = "references/ponytail-license.txt"
            self.assertEqual(
                (SKILL / relative_license).read_bytes(),
                (home / ".agents/skills/codex-prove" / relative_license).read_bytes(),
            )
            uninstall = subprocess.run(
                ["bash", "scripts/uninstall.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertEqual(0, uninstall.returncode, uninstall.stdout)
            self.assertEqual(before, (config.read_bytes(), other.read_bytes()))
            for source in profiles:
                with self.subTest(removed_profile=source.stem):
                    self.assertFalse((home / ".codex" / "agents" / source.name).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
