#!/usr/bin/env python3
"""Evidence safety regressions and the retained v1.0 benchmark manifest.

Text guards protect critical policy boundaries, not model behavior. See the
v1.1 live probe record for observed execution; do not count fixtures as live tests.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/codex-prove"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class EvidenceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = " ".join(read(SKILL / "references/orchestration.md").split())
        cls.runtime = " ".join(read(SKILL / "references/runtime-notes.md").split())

    def test_evidence_is_about_candidate_and_requirement_not_transport(self) -> None:
        self.assertIn("Transport `completed` is not acceptance", self.protocol)
        self.assertIn("invalidate affected evidence only", self.protocol)
        self.assertIn("Verify the verifier", self.protocol)
        self.assertIn("PASS requires all requested criteria", self.protocol)
        self.assertIn("wrong scope", self.protocol)

    def test_missing_structure_is_repairable_not_an_automatic_gate(self) -> None:
        self.assertIn("Equivalent concise formats", self.protocol)
        self.assertIn("missing heading or optional field is not BLOCKED", self.protocol)
        self.assertIn("result-only follow-up (no new writes)", self.protocol)
        self.assertIn("run the missing check inside existing authority", self.protocol)

    def test_handoff_requires_process_quiescence_and_preserves_work(self) -> None:
        self.assertIn("all its mutating command processes have ended", self.protocol)
        self.assertIn("timeout or an interrupt request alone does not prove quiescence", self.protocol)
        self.assertIn("preserves the actual diff and unrelated user changes", self.protocol)
        self.assertIn("attempt history", self.protocol)
        self.assertNotIn("Never transfer a file after its owner", self.protocol)

    def test_recovery_is_progress_bounded_without_renewed_routine_approval(self) -> None:
        self.assertIn("consecutive no-progress attempts", self.protocol)
        self.assertIn("do not", self.runtime.lower())
        self.assertIn("without repeated user approval", self.runtime)
        self.assertIn("never route around a denied action", self.runtime.lower())
        self.assertIn("same-scope Delta", self.protocol)

    def test_no_self_attestation_or_mandatory_idle_turn(self) -> None:
        self.assertIn("complete task may be sent on the first turn", self.runtime)
        self.assertIn("No identity-only handshake", self.runtime)
        self.assertIn("authoritative Host/tool role mapping", self.runtime)
        self.assertIn("actual launch record", self.runtime)
        self.assertIn("not a successfully selected custom agent", self.runtime)
        self.assertIn("do not claim exact-profile execution", self.runtime)

    def test_simplification_does_not_remove_required_safety_or_behavior(self) -> None:
        self.assertIn("must not silently replace an explicitly requested feature", self.protocol)
        for boundary in ("validation", "error handling", "accessibility", "regression checks"):
            self.assertIn(boundary, self.protocol)
        self.assertIn("not another phase", self.protocol)
        self.assertIn("does not launch a separate simplification reviewer", self.protocol)
        self.assertIn("snapshots show net changes, not who wrote", self.protocol)


class HistoricalBenchmarkManifestTests(unittest.TestCase):
    def test_ab_protocol_is_reproducible_and_claim_free(self) -> None:
        data = json.loads(read(ROOT / "tests/fixtures/v100-ab-benchmark.json"))
        self.assertEqual(1, data["schema_version"])
        self.assertEqual("protocol_only", data["evidence_class"])
        self.assertEqual({"baseline", "candidate"}, {arm["id"] for arm in data["arms"]})
        self.assertGreaterEqual(data["repetitions"], 3)
        for key in ("counterbalanced_order", "fresh_isolated_checkout", "hidden_grader_after_run"):
            self.assertTrue(data[key])
        self.assertNotIn("winner", data)
        self.assertNotIn("results", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
