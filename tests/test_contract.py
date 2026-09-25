#!/usr/bin/env python3
"""Structural contracts; behavioral claims require the separate live probes."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-prove"
COMPAT = ROOT / ".agents" / "skills" / "sol-control"
CONTROLLER = ROOT / ".codex" / "agents" / "prove-controller.toml"
COMPLEX = ROOT / ".codex" / "agents" / "prove-complex-worker.toml"
EFFICIENT = ROOT / ".codex" / "agents" / "prove-efficient-worker.toml"
SPECIALIST = ROOT / ".codex" / "agents" / "prove-specialist-worker.toml"
REPO_URL = "https://github.com/yehyakin/codex-prove"


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


class RepositoryStructureTests(unittest.TestCase):
    def test_canonical_skill_structure_exists(self) -> None:
        for path in (
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "orchestration.md",
            SKILL / "references" / "runtime-notes.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_compatibility_entry_is_small_and_has_no_second_protocol(self) -> None:
        self.assertTrue((COMPAT / "SKILL.md").is_file())
        self.assertTrue((COMPAT / "agents" / "openai.yaml").is_file())
        self.assertFalse((COMPAT / "references").exists())
        self.assertLess(len(read(COMPAT / "SKILL.md").splitlines()), 30)

    def test_only_model_neutral_agent_source_names_exist(self) -> None:
        names = sorted(path.name for path in (ROOT / ".codex" / "agents").glob("*.toml"))
        self.assertEqual(
            ["prove-complex-worker.toml", "prove-controller.toml", "prove-efficient-worker.toml", "prove-specialist-worker.toml"],
            names,
        )

    def test_public_docs_use_new_repository_url(self) -> None:
        for path in (ROOT / "README.md", ROOT / "README.en.md", ROOT / "SECURITY.md"):
            text = read(path)
            self.assertIn(REPO_URL, text, path.name)
            self.assertNotIn("github.com/yehyakin/codex-sol-control", text, path.name)

    def test_required_release_files_exist(self) -> None:
        for relative in (
            "CODEX_PROVE_V1_IMPLEMENTATION_REPORT.md",
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md",
            "scripts/install.sh", "scripts/uninstall.sh", "scripts/validate.sh",
            "scripts/install.ps1", "scripts/uninstall.ps1", "scripts/validate.ps1",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


class InvocationAndLanguageTests(unittest.TestCase):
    def test_canonical_frontmatter_is_explicit_only(self) -> None:
        text = read(SKILL / "SKILL.md")
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name:\s*codex-prove\s*$")
        self.assertRegex(frontmatter, r"(?m)^description:\s*Use only when\b")
        self.assertIn("$codex-prove", frontmatter)

    def test_canonical_interface_disables_implicit_invocation(self) -> None:
        text = read(SKILL / "agents" / "openai.yaml")
        self.assertIn('display_name: "Codex PROVE"', text)
        self.assertIn("$codex-prove", text)
        self.assertRegex(text, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_legacy_alias_redirects_without_implicit_invocation(self) -> None:
        text = read(COMPAT / "SKILL.md") + read(COMPAT / "agents" / "openai.yaml")
        self.assertIn("$sol-control", text)
        self.assertIn("$codex-prove", text)
        self.assertIn("deprecated", text)
        self.assertRegex(text, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_runtime_defaults_to_chinese(self) -> None:
        self.assertIn("中文", read(SKILL / "SKILL.md"))
        for path in (CONTROLLER, SPECIALIST, COMPLEX, EFFICIENT):
            with path.open("rb") as handle:
                instructions = tomllib.load(handle)["developer_instructions"]
            self.assertIn("中文", instructions, path.name)
            self.assertIn("其他语言", instructions, path.name)

    def test_readme_default_is_chinese_with_english_peer(self) -> None:
        self.assertIn("运行时默认使用简体中文", read(ROOT / "README.md"))
        self.assertIn("Runtime output defaults to Simplified Chinese", read(ROOT / "README.en.md"))


class ProtocolStructureTests(unittest.TestCase):
    def test_graph_and_review_examples_have_stable_integration_fields(self) -> None:
        # These are template shape checks, not proof of model behavior.
        text = read(SKILL / "references" / "orchestration.md")
        for field in (
            "goal", "done_when", "tasks", "stages", "integration_owner",
            "dependencies", "read_scope", "write_scope", "can_launch", "held_reason",
            "requirements_coverage", "required_fixes", "evidence_quality",
        ):
            self.assertRegex(text, rf"(?m)^\s*{field}:\s*", field)
        self.assertIn("verdict: PASS | FIX | BLOCKED", text)

    def test_runtime_is_not_preloaded_for_direct_work(self) -> None:
        text = read(SKILL / "SKILL.md")
        self.assertLess(len(text.splitlines()), 120)
        self.assertIn("zero agents", text)
        self.assertIn("Do not preload every reference for Direct work", text)
        self.assertIn("including a small task with an explicit invocation", text)
        self.assertNotIn("An explicit invocation always starts with the controller", text)

    def test_guidance_and_license_travel_with_the_skill(self) -> None:
        notice = SKILL / "references" / "ponytail-license.txt"
        text = read(notice)
        self.assertIn("Copyright (c) 2026 DietrichGebert", text)
        self.assertIn("Permission is hereby granted", text)
        self.assertIn("THE SOFTWARE IS PROVIDED", text)
        self.assertIn("ponytail-license.txt", read(SKILL / "references" / "orchestration.md"))
        self.assertIn("DietrichGebert/ponytail", read(ROOT / "NOTICE"))
        self.assertFalse((SKILL / "hooks").exists())

    def test_skill_contains_no_business_project_terms(self) -> None:
        text = contract() + read(COMPAT / "SKILL.md")
        for forbidden in ("IPZOR", "Buzz", "DeepSeek", "OpenPencil"):
            self.assertNotRegex(text, re.compile(forbidden, re.I))


if __name__ == "__main__":
    unittest.main(verbosity=2)
