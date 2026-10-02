"""Offline checks only: regular CI never launches a paid model."""
import json
import os
import hashlib
import sys
from pathlib import Path
import tempfile
import unittest

import worker_model_pilot as pilot


class WorkerPilotTests(unittest.TestCase):
    def read_usage(self, events, **options):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
            return pilot.parse_usage(path, **options)

    def completion(self, **identity):
        return {"type": "turn.completed", "usage": {
            "input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 10}, **identity}

    def test_identified_completion_is_counted_once(self):
        event = self.completion(thread_id="root", turn_id="turn-1")
        result = self.read_usage([event, event])
        self.assertEqual(100, result["usage"]["input_tokens"])
        self.assertEqual(1, result["duplicate_events_ignored"])
        self.assertEqual("root_cli_stream_only", result["usage_scope"])
        self.assertIsNone(result["whole_run_usage"])

    def test_equal_counts_on_different_turns_are_not_duplicates(self):
        result = self.read_usage([self.completion(turn_id="one"), self.completion(turn_id="two")])
        self.assertEqual(200, result["usage"]["input_tokens"])
        self.assertEqual(0, result["duplicate_events_ignored"])

    def test_conflicting_duplicate_is_not_a_total(self):
        event = self.completion(thread_id="root", turn_id="one")
        other = event | {"usage": event["usage"] | {"input_tokens": 120}}
        result = self.read_usage([event, other])
        self.assertIsNone(result["usage"])
        self.assertIsNone(result["observed_completed_usage"])
        self.assertIn("conflicting_completion_identity", result["usage_issues"])

    def test_cli_lifecycle_identifies_turns_without_turn_ids(self):
        start = {"type": "turn.started"}
        event = self.completion()
        result = self.read_usage([{"type": "thread.started", "thread_id": "root"},
                                  start, event, event, start, event])
        self.assertEqual(200, result["usage"]["input_tokens"])
        self.assertEqual(1, result["duplicate_events_ignored"])
        self.assertTrue(result["usage_complete_for_scope"])

    def test_unidentifiable_multiple_completions_are_unknown(self):
        result = self.read_usage([self.completion(), self.completion()])
        self.assertIsNone(result["usage"])
        self.assertIn("unidentified_multiple_completions", result["usage_issues"])

    def test_completion_identity_must_agree_with_the_active_turn(self):
        result = self.read_usage([{"type": "turn.started", "turn_id": "one"},
                                  self.completion(turn_id="two")])
        self.assertIsNone(result["usage"])
        self.assertIn("mismatched_turn_identity", result["usage_issues"])

    def test_late_explicit_identity_does_not_double_count_replay(self):
        result = self.read_usage([{"type": "turn.started"},
                                  self.completion(turn_id="one"), self.completion()])
        self.assertEqual(100, result["usage"]["input_tokens"])
        self.assertEqual(1, result["duplicate_events_ignored"])
        # An ID arriving only in a second completion could be an enriched replay
        # or a different turn with a missing start. Do not silently add both.
        ambiguous = self.read_usage([{"type": "turn.started"},
                                     self.completion(), self.completion(turn_id="one")])
        self.assertIsNone(ambiguous["usage"])
        self.assertIn("ambiguous_completion_identity", ambiguous["usage_issues"])

    def test_overlapping_starts_leave_usage_unknown(self):
        result = self.read_usage([{"type": "turn.started"}, {"type": "turn.started"}, self.completion()])
        self.assertIsNone(result["usage"])
        self.assertIn("overlapping_turn_lifecycle", result["usage_issues"])

    def test_failure_or_incomplete_lifecycle_preserves_only_known_successes(self):
        for tail in ([{"type": "turn.failed"}], [{"type": "error"}], [{"type": "turn.started"}]):
            with self.subTest(tail=tail):
                result = self.read_usage([self.completion(turn_id="one"), *tail])
                self.assertIsNone(result["usage"])
                self.assertEqual(100, result["observed_completed_usage"]["input_tokens"])
                self.assertFalse(result["usage_complete_for_scope"])
                self.assertIsNone(result["whole_run_usage"])

    def test_unsuccessful_process_cannot_claim_complete_usage(self):
        result = self.read_usage([self.completion()], process_complete=False)
        self.assertIsNone(result["usage"])
        self.assertEqual(100, result["observed_completed_usage"]["input_tokens"])
        self.assertIn("process_incomplete", result["usage_issues"])

    def test_child_activity_does_not_make_root_usage_whole_run(self):
        result = self.read_usage([{"type": "item.completed", "item": {
            "type": "collab_tool_call", "tool": "spawn_agent", "receiver_thread_ids": ["child"]}},
            self.completion()])
        self.assertEqual(100, result["usage"]["input_tokens"])
        self.assertIsNone(result["whole_run_usage"])
        self.assertEqual("root_cli_stream_only", result["usage_scope"])

    def test_mixed_thread_stream_cannot_be_silently_aggregated(self):
        result = self.read_usage([self.completion(thread_id="root", turn_id="one"),
                                  self.completion(thread_id="child", turn_id="one")])
        self.assertIsNone(result["usage"])
        self.assertIn("mixed_thread_stream", result["usage_issues"])

    def test_repeated_thread_start_is_not_a_new_billable_turn_identity(self):
        block = [{"type": "thread.started", "thread_id": "root"},
                 {"type": "turn.started"}, self.completion()]
        for events in (block + block, [block[0], *block]):
            with self.subTest(events=events):
                result = self.read_usage(events)
                self.assertIsNone(result["usage"])
                self.assertFalse(result["usage_complete_for_scope"])
                self.assertIn("repeated_thread_start", result["usage_issues"])

    def test_invalid_event_type_cannot_be_ignored_in_a_complete_stream(self):
        for event in ({}, {"type": None}, {"type": []}, {"type": ""}):
            with self.subTest(event=event):
                result = self.read_usage([event, self.completion()])
                self.assertIsNone(result["usage"])
                self.assertIn("invalid_event_type", result["usage_issues"])

    def test_failed_turn_closes_before_recovery_and_keeps_successful_subset(self):
        result = self.read_usage([{"type": "turn.started"}, {"type": "turn.failed"},
                                  {"type": "turn.started"}, self.completion()])
        self.assertIsNone(result["usage"])
        self.assertEqual(100, result["observed_completed_usage"]["input_tokens"])
        self.assertEqual(["failed_turn_usage_unknown"], result["usage_issues"])

    def test_malformed_stream_cannot_appear_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            path.write_text(json.dumps(self.completion()) + '\n{"type":')
            result = pilot.parse_usage(path)
        self.assertIsNone(result["usage"])
        self.assertIn("malformed_jsonl", result["usage_issues"])

    def test_invalid_identity_and_counters_are_not_coerced(self):
        event = self.completion(turn_id="one")
        for bad in (event | {"turn_id": []}, event | {"thread_id": 3},
                    event | {"usage": event["usage"] | {"input_tokens": True}},
                    event | {"usage": event["usage"] | {"output_tokens": -1}}):
            with self.subTest(event=bad):
                self.assertIsNone(self.read_usage([bad])["usage"])

    def test_archived_inputs_and_candidates_match_recorded_hashes(self):
        archive = json.loads((pilot.ROOT / "docs/research/worker-pilot-2026-09-25.json").read_text(encoding="utf-8"))
        fixtures = {case["id"]: case for case in archive["frozen_fixtures"]}
        for row in archive["results"]["cells"]:
            case = fixtures[row["case_id"]]
            ident = f"{row['case_id']}-{row['model_requested']}-r{row['repetition']}"
            files = case["files"] | archive["candidate_sources"][ident]
            hashes = {name: hashlib.sha256(body.encode("utf-8")).hexdigest()
                      for name, body in files.items()}
            self.assertEqual(pilot.digest(hashes), row["candidate_identity"])
            self.assertEqual(pilot.digest(case["grader"]), row["grader_sha256"])
            self.assertEqual(pilot.digest(archive["frozen_prompts"][row["case_id"]]), row["prompt_sha256"])
        self.assertEqual(archive["summary"], pilot.summarize(archive["results"]["cells"]))

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_every_grader_rejects_broken_and_accepts_oracle(self):
        with tempfile.TemporaryDirectory(prefix="prove-pilot-calibration-") as temp:
            for case in pilot.cases():
                with self.subTest(case=case["id"]):
                    result = pilot.calibrate(case, Path(temp) / case["id"])
                    self.assertTrue(result["pass"], result)

    def test_counterbalanced_complete_schedule(self):
        cells = list(pilot.schedule())
        self.assertEqual(len(cells), 18)
        self.assertEqual(len({(c["id"], m, r) for c, m, r in cells}), 18)
        self.assertEqual(cells[0][1], cells[7][1])
        self.assertNotEqual(cells[0][1], cells[6][1])

    def test_missing_or_invalid_usage_is_unknown_not_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            for event in ({"type": "turn.failed"}, {"type": "turn.completed"},
                          {"type": "turn.completed", "usage": None},
                          {"type": "turn.completed", "usage": []},
                          None, [],
                          {"type": "turn.completed", "usage": {
                              "input_tokens": 1, "cached_input_tokens": 2, "output_tokens": 0}}):
                path.write_text(json.dumps(event) + "\n")
                self.assertIsNone(pilot.parse_usage(path)["usage"])
            path.write_text(json.dumps({"type": "turn.completed", "usage": {
                "input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 10}}) + "\n")
            self.assertEqual(pilot.parse_usage(path)["usage"]["input_tokens"], 100)

    def test_unknown_cost_and_incomplete_run_have_no_winner(self):
        summary = pilot.summarize([])
        self.assertFalse(summary["complete"])
        self.assertIsNone(summary["winner"])
        self.assertIsNone(summary["measured_cost"])

    def test_snapshot_detects_unowned_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspace"
            pilot.seed(workspace, {"a.py": "original\n", "user-notes.txt": "keep\n"})
            before = pilot.snapshot(workspace)
            (workspace / "user-notes.txt").write_text("changed\n")
            self.assertEqual(pilot.changed(before, pilot.snapshot(workspace)), ["user-notes.txt"])
            (workspace / "__pycache__").mkdir()
            (workspace / "__pycache__/a.pyc").write_bytes(b"untracked bytecode")
            self.assertIn("__pycache__/a.pyc", pilot.changed(before, pilot.snapshot(workspace)))

    def test_snapshot_detects_unowned_empty_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspace"
            pilot.seed(workspace, {"a.py": "original\n"})
            before = pilot.snapshot(workspace)
            (workspace / "unowned").mkdir()
            self.assertEqual(pilot.changed(before, pilot.snapshot(workspace)), ["unowned"])

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_candidate_cannot_replace_unittest_runner_with_success_stub(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = pilot.cases()[0]
            files = case["files"] | {"settings.py": (
                "import unittest\ndef migrate(settings): return None\n"
                "def fake(self, result=None):\n"
                " result.startTest(self)\n result.addSuccess(self)\n result.stopTest(self)\n"
                " return result\nunittest.TestCase.run = fake\n")}
            pilot.seed(root / "work", files)
            for public in (False, True):
                with self.subTest(public=public):
                    result = pilot.grade(case, root / "work", root, public=public)
                    self.assertFalse(result["pass"], result)
                    self.assertIn("test framework was modified", (root / "grade.stderr").read_text())

    def test_mismatched_prompt_cannot_be_summarized(self):
        base = {"case_id": "x", "model_requested": pilot.MODELS[0], "repetition": 1,
                "base_sha256": "a", "prompt_sha256": "b", "grader_sha256": "c"}
        other = base | {"model_requested": pilot.MODELS[1], "prompt_sha256": "different"}
        with self.assertRaisesRegex(ValueError, "unmatched"):
            pilot.summarize([base, other])

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_valid_extra_helper_call_is_not_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = pilot.cases()[2]
            files = case["files"] | case["oracle"]
            files["exporter.py"] = files["exporter.py"].replace(
                "return records_to_csv(projected, fields)",
                "records_to_csv([], fields)\n    return records_to_csv(projected, fields)")
            pilot.seed(root / "work", files)
            self.assertTrue(pilot.grade(case, root / "work", root)["pass"])

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_external_grade_that_mutates_candidate_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pilot.seed(root / "work", {"a.py": "original\n"})
            case = {"expected_checks": 1, "grader": (
                "from pathlib import Path\nPath('a.py').write_text('changed')\n"
                "import unittest\nclass Checks(unittest.TestCase):\n"
                " def test_ok(self): self.assertTrue(True)\n")}
            result = pilot.grade(case, root / "work", root)
            self.assertEqual(result["exit_code"], 0)
            self.assertFalse(result["pass"])

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_early_exit_zero_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pilot.seed(root / "work", {"settings.py": "raise SystemExit(0)\n"})
            result = pilot.grade(pilot.cases()[0], root / "work", root)
            self.assertEqual(result["exit_code"], 0)
            self.assertFalse(result["pass"])

    @unittest.skipUnless(sys.platform == "darwin", "Real macOS sandbox check")
    def test_live_grader_cannot_write_outside_the_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pilot.seed(root / "work", {"settings.py": "from pathlib import Path\n"
                       f"Path({str(root / 'outside')!r}).write_text('bad')\n"})
            result = pilot.grade(pilot.cases()[0], root / "work", root, live=True)
            self.assertFalse(result["pass"])
            self.assertFalse((root / "outside").exists())

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_wrong_defaults_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = pilot.cases()[0]
            files = case["files"] | case["oracle"]
            files["settings.py"] = files["settings.py"].replace('("limit", "max_workers", 2)',
                                                               '("limit", "max_workers", 999)')
            pilot.seed(root / "work", files)
            self.assertFalse(pilot.grade(case, root / "work", root)["pass"])

    @unittest.skipUnless(os.name == "posix", "Pilot process supervision is POSIX-only")
    def test_shared_alias_loss_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = pilot.cases()[0]
            files = case["files"] | case["oracle"]
            files["settings.py"] = files["settings.py"].replace(
                'workers = dict(result.get("workers", {}))',
                'workers = result.get("workers", {})')
            pilot.seed(root / "work", files)
            self.assertFalse(pilot.grade(case, root / "work", root)["pass"])


if __name__ == "__main__":
    unittest.main()
