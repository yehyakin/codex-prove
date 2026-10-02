#!/usr/bin/env python3
"""Deterministic tests for the matched A/B evidence harness."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmark_ab.py"
MANIFEST = ROOT / "tests" / "fixtures" / "v100-ab-benchmark.json"


def load_module():
    spec = importlib.util.spec_from_file_location("benchmark_ab", SCRIPT)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise RuntimeError("cannot load benchmark_ab.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BenchmarkABTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.manifest = cls.module.validate_manifest(json.loads(MANIFEST.read_text(encoding="utf-8")))
        cls.schedule = cls.module.make_schedule(cls.manifest)

    def make_results(self) -> dict:
        cells = []
        for cell in self.schedule["cells"]:
            cells.append(
                {
                    "case_id": cell["case_id"],
                    "arm": cell["arm"],
                    "repetition": cell["repetition"],
                    "base_commit": "a" * 40,
                    "prompt_sha256": "b" * 64,
                    "grader_sha256": "c" * 64,
                    "candidate_identity": "d" * 64,
                    "held_out_pass": cell["arm"] == "candidate",
                    "integrity_pass": True,
                    "false_pass": cell["arm"] == "baseline",
                    "input_tokens": 100 if cell["arm"] == "baseline" else 80,
                    "output_tokens": 20,
                    "elapsed_seconds": 10.0 if cell["arm"] == "baseline" else 9.0,
                    "cost_value": 1.0 if cell["arm"] == "baseline" else 0.8,
                    "cost_unit": "credits",
                    "subagent_count": 1,
                    "retry_count": 0,
                }
            )
        return {
            "schema_version": 1,
            "evidence_class": "measured_ab_cells",
            "manifest_sha256": self.schedule["manifest_sha256"],
            "cells": cells,
        }

    def test_schedule_is_complete_unique_and_counterbalanced(self) -> None:
        cells = self.schedule["cells"]
        expected = len(self.manifest["cases"]) * len(self.manifest["arms"]) * self.manifest["repetitions"]
        self.assertEqual(expected, len(cells))
        keys = {(cell["case_id"], cell["arm"], cell["repetition"]) for cell in cells}
        self.assertEqual(expected, len(keys))

        first_arm_by_case_and_rep = {
            (cell["case_id"], cell["repetition"]): cell["arm"]
            for cell in cells
            if cell["order"] == 1
        }
        for case in self.manifest["cases"]:
            observed = {
                first_arm_by_case_and_rep[(case["id"], repetition)]
                for repetition in range(1, self.manifest["repetitions"] + 1)
            }
            self.assertEqual({"baseline", "candidate"}, observed)

    def test_summary_reports_both_arms_without_declaring_a_winner(self) -> None:
        rows = self.module.validate_results(self.manifest, self.schedule, self.make_results())
        summary = self.module.summarize(self.manifest, rows)
        self.assertIsNone(summary["winner"])
        self.assertEqual(0.0, summary["arms"]["baseline"]["held_out_pass_rate"])
        self.assertEqual(1.0, summary["arms"]["candidate"]["held_out_pass_rate"])
        self.assertEqual(1.0, summary["arms"]["baseline"]["false_pass_rate"])
        self.assertEqual(0.0, summary["arms"]["candidate"]["false_pass_rate"])
        self.assertLess(
            summary["arms"]["candidate"]["input_tokens_total"],
            summary["arms"]["baseline"]["input_tokens_total"],
        )

    def test_incomplete_cells_fail_closed(self) -> None:
        results = self.make_results()
        results["cells"].pop()
        with self.assertRaisesRegex(self.module.ContractError, "missing 1 scheduled result cells"):
            self.module.validate_results(self.manifest, self.schedule, results)

    def test_pair_rejects_different_inputs_or_grader(self) -> None:
        for field in ("base_commit", "prompt_sha256", "grader_sha256"):
            with self.subTest(field=field):
                results = self.make_results()
                results["cells"][0][field] = "e" * len(results["cells"][0][field])
                with self.assertRaisesRegex(self.module.ContractError, "paired .* mismatch"):
                    self.module.validate_results(self.manifest, self.schedule, results)

    def test_missing_cost_stays_unknown_without_crashing(self) -> None:
        results = self.make_results()
        results["cells"][0].update(cost_value=None, cost_unit=None)
        rows = self.module.validate_results(self.manifest, self.schedule, results)
        summary = self.module.summarize(self.manifest, rows)
        arm = summary["arms"][results["cells"][0]["arm"]]
        self.assertIsNone(arm["cost_value_total"])
        self.assertIsNone(arm["cost_unit"])
        self.assertEqual(arm["runs"] - 1, arm["cost_observed_runs"])

    def test_unknown_cost_is_distinct_from_observed_zero(self) -> None:
        results = self.make_results()
        for cell in results["cells"]:
            if cell["arm"] == "baseline":
                cell.update(cost_value=None, cost_unit=None)
            else:
                cell["cost_value"] = 0
        rows = self.module.validate_results(self.manifest, self.schedule, results)
        arms = self.module.summarize(self.manifest, rows)["arms"]
        self.assertIsNone(arms["baseline"]["cost_value_total"])
        self.assertIsNone(arms["baseline"]["cost_unit"])
        self.assertEqual(0, arms["baseline"]["cost_observed_runs"])
        self.assertEqual(0, arms["candidate"]["cost_value_total"])
        self.assertEqual("credits", arms["candidate"]["cost_unit"])
        self.assertEqual(arms["candidate"]["runs"], arms["candidate"]["cost_observed_runs"])

    def test_cross_arm_units_are_not_comparable(self) -> None:
        results = self.make_results()
        for cell in results["cells"]:
            if cell["arm"] == "candidate":
                cell["cost_unit"] = "USD"
        rows = self.module.validate_results(self.manifest, self.schedule, results)
        with self.assertRaisesRegex(self.module.ContractError, "mixed cost units across arms"):
            self.module.summarize(self.manifest, rows)

    def test_legacy_protocol_cannot_claim_autonomous_routing(self) -> None:
        rows = self.module.validate_results(self.manifest, self.schedule, self.make_results())
        summary = self.module.summarize(self.manifest, rows)
        self.assertEqual("fixed_settings", summary["routing_scope"])
        self.assertFalse(summary["autonomous_routing_declared"])

    def test_autonomous_protocol_requires_explicit_unconstrained_declaration(self) -> None:
        manifest = dict(self.manifest, routing_scope="autonomous")
        for declaration in (None, False, "true", 1):
            with self.subTest(declaration=declaration):
                manifest["routing_unconstrained"] = declaration
                with self.assertRaisesRegex(self.module.ContractError, "routing_unconstrained"):
                    self.module.validate_manifest(manifest)
        manifest["routing_unconstrained"] = True
        self.module.validate_manifest(manifest)
        schedule = self.module.make_schedule(manifest)
        results = self.make_results()
        results["manifest_sha256"] = schedule["manifest_sha256"]
        rows = self.module.validate_results(manifest, schedule, results)
        summary = self.module.summarize(manifest, rows)
        self.assertEqual("autonomous", summary["routing_scope"])
        self.assertTrue(summary["autonomous_routing_declared"])
        self.assertNotIn("autonomous_routing_evidence", summary)
        self.assertIsNone(summary["winner"])

    def test_invalid_routing_scope_fails_closed(self) -> None:
        for scope in (None, [], {}, False, "unsupported"):
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(self.module.ContractError, "unsupported routing_scope"):
                    self.module.validate_manifest(dict(self.manifest, routing_scope=scope))

    def test_nonfinite_metrics_fail_closed(self) -> None:
        for field in ("cost_value", "elapsed_seconds"):
            for value in (float("nan"), float("inf"), float("-inf"), 10 ** 400):
                with self.subTest(field=field, value=value):
                    results = self.make_results()
                    results["cells"][0][field] = value
                    with self.assertRaises(self.module.ContractError):
                        self.module.validate_results(self.manifest, self.schedule, results)

    def test_nonfinite_aggregate_metrics_fail_closed(self) -> None:
        for field in ("cost_value", "elapsed_seconds"):
            with self.subTest(field=field):
                results = self.make_results()
                for cell in results["cells"]:
                    cell[field] = 1e308
                rows = self.module.validate_results(self.manifest, self.schedule, results)
                with self.assertRaisesRegex(self.module.ContractError, "nonfinite .*_total"):
                    self.module.summarize(self.manifest, rows)

    def test_cli_summary_keeps_unknown_cost_and_rejects_mismatched_pairs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="codex-prove-ab.") as raw:
            result_path = Path(raw) / "results.json"
            data = self.make_results()
            data["cells"][0].update(cost_value=None, cost_unit=None)
            for mismatch in (False, True):
                with self.subTest(mismatch=mismatch):
                    if mismatch:
                        data["cells"][0]["prompt_sha256"] = "e" * 64
                    result_path.write_text(json.dumps(data), encoding="utf-8")
                    run = subprocess.run(
                        [sys.executable, str(SCRIPT), "summarize", str(MANIFEST), str(result_path)],
                        cwd=ROOT, text=True, capture_output=True, check=False,
                    )
                    if mismatch:
                        self.assertEqual(2, run.returncode, run.stderr)
                        self.assertEqual("", run.stdout)
                        self.assertIn("paired prompt_sha256 mismatch", run.stderr)
                        self.assertNotIn("Traceback", run.stderr)
                    else:
                        self.assertEqual(0, run.returncode, run.stderr)
                        arm = json.loads(run.stdout)["arms"][data["cells"][0]["arm"]]
                        self.assertIsNone(arm["cost_value_total"])
                        self.assertEqual(arm["runs"] - 1, arm["cost_observed_runs"])

    def test_cli_validate_emits_frozen_manifest_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="codex-prove-ab.") as raw:
            output = Path(raw) / "validation.json"
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "validate", str(MANIFEST), "--output", str(output)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(0, run.returncode, run.stdout)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("PASS", data["status"])
            self.assertEqual(self.schedule["manifest_sha256"], data["manifest_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
