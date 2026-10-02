#!/usr/bin/env python3
"""Candidate profile, validator and migration checks; not live model evaluation."""

from __future__ import annotations

import hashlib
import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DEFAULTS = {
    "prove-controller": ("gpt-6.1-sol", "high", "read-only"),
    "prove-complex-worker": ("gpt-6.1-sol", "high", "workspace-write"),
    "prove-specialist-worker": ("gpt-6-astra", "high", "read-only"),
    "prove-efficient-worker": ("gpt-6-luna", "max", "workspace-write"),
}


class Sol61CandidateTests(unittest.TestCase):
    def test_default_profiles_match_release_mapping(self):
        # Release defaults are regression-tested here, not imposed on users by
        # installation validation. test_source_validation covers custom profiles.
        for name, (model, effort, sandbox) in PROFILE_DEFAULTS.items():
            data = tomllib.loads((ROOT / ".codex/agents" / (name + ".toml")).read_text(encoding="utf-8"))
            expected = dict(name=name, model=model, model_reasoning_effort=effort, sandbox_mode=sandbox)
            self.assertEqual(expected, {key: data[key] for key in expected})
        self.assertEqual(3, len({model for model, _, _ in PROFILE_DEFAULTS.values()}))

    def test_old_live_receipt_is_immutable_and_not_candidate_proof(self):
        source = (ROOT / "docs/release/v1.1.0-runtime.json").read_bytes()
        self.assertEqual("3175d8e51484d54d9b2928ad721586ec1177fb569bee30fbb0460024628b61ce",
                         hashlib.sha256(source.replace(b"\r\n", b"\n")).hexdigest())
        receipt = json.loads(source)
        self.assertEqual("v1.1.0", receipt["release"])
        self.assertNotIn("gpt-6.1-sol", {launch["model"] for launch in receipt["runtime"]["launches"]})
        candidate = (ROOT / ".codex/agents/prove-controller.toml").read_bytes().replace(b"\r\n", b"\n")
        self.assertNotEqual(receipt["source_runtime_sha256"][".codex/agents/prove-controller.toml"],
                            hashlib.sha256(candidate).hexdigest())

    def test_forward_inputs_are_fresh_requests_not_answer_keys(self):
        cases = []
        for filename, count in (("sol61-forward-inputs.json", 16), ("sol61-followup-inputs.json", 4)):
            batch = json.loads((ROOT / "tests/fixtures" / filename).read_text(encoding="utf-8"))
            self.assertEqual(count, len(batch), filename)
            cases.extend(batch)
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        for case in cases:
            self.assertEqual({"id", "request", "context"}, set(case))
            self.assertTrue(all(isinstance(value, str) and value.strip() for value in case.values()))
        # This validates test material, not the decisions made by a model.

    def test_candidate_has_no_extra_runtime_framework_or_agent_ids(self):
        profiles = {path.stem for path in (ROOT / ".codex/agents").glob("*.toml")}
        self.assertEqual(set(PROFILE_DEFAULTS), profiles)
        canonical = ROOT / ".agents/skills/codex-prove"
        self.assertFalse((canonical / "hooks").exists())
        self.assertFalse((canonical / "scripts").exists())

    def test_routing_regression_inputs_are_separate_from_the_grading_rubric(self):
        # Fixture integrity only: the policy's decisions still need forward evaluation.
        cases = json.loads((ROOT / "tests/fixtures/sol61-routing-regressions.json").read_text(encoding="utf-8"))
        self.assertEqual(14, len(cases))
        self.assertEqual(14, len({case["id"] for case in cases}))
        for case in cases:
            self.assertEqual({"id", "request", "context"}, set(case))
            self.assertTrue(all(isinstance(value, str) and value.strip() for value in case.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
