"""Small, synthetic maintenance cases; never installed with the Skill.

Prompts disclose every requirement. Post-run checks and oracle fixes are not
included in worker workspaces or prompts. No upstream implementation is copied.
"""

from textwrap import dedent


def source(text):
    return dedent(text).lstrip()


CASES = [
    {
        "id": "settings_migration",
        "expected_checks": 5,
        "objective": "Repair the v1-to-v2 settings migration without changing user settings.",
        "requirements": """
Implement migrate(settings) in settings.py. Input is a dict; legacy 'workers'
and current 'execution', when present, must be dicts (otherwise ValueError).
Return a deep-independent copy with schema_version=2 and an execution dict.
Map workers.limit to execution.max_workers and workers.enabled to
execution.enabled only when the corresponding destination key is absent.
Existing destination values, including 0, False and None, win. If neither source
nor destination supplies a value, default max_workers=2 and enabled=True.
Remove only workers.limit and workers.enabled; preserve every other key and
nested value, including unknown workers fields. Remove workers only if empty.
Do not mutate the input or share mutable nested values. Applying migrate twice
must produce the same value. Do not add dependencies or change the public API.
""",
        "owned": ["settings.py", "test_settings.py"],
        "files": {
            "settings.py": source('''
                def migrate(settings):
                    result = dict(settings)
                    workers = result.pop("workers", {})
                    result["execution"] = {
                        "max_workers": workers.get("limit", 2),
                        "enabled": workers.get("enabled", True),
                    }
                    result["schema_version"] = 2
                    return result
            '''),
            "test_settings.py": source('''
                import unittest
                from settings import migrate

                class MigrationTests(unittest.TestCase):
                    def test_defaults(self):
                        self.assertEqual(migrate({}), {
                            "schema_version": 2,
                            "execution": {"max_workers": 2, "enabled": True},
                        })

                if __name__ == "__main__":
                    unittest.main()
            '''),
        },
        "oracle": {
            "settings.py": source('''
                from copy import deepcopy

                def migrate(settings):
                    if not isinstance(settings, dict):
                        raise ValueError("settings must be a dict")
                    for key in ("workers", "execution"):
                        if key in settings and not isinstance(settings[key], dict):
                            raise ValueError(key + " must be a dict")
                    result = deepcopy(settings)
                    # Detach the sections being transformed so aliases under
                    # unknown keys keep their original values in the output.
                    workers = dict(result.get("workers", {}))
                    execution = dict(result.get("execution", {}))
                    result["execution"] = execution
                    for old, new, default in (
                        ("limit", "max_workers", 2),
                        ("enabled", "enabled", True),
                    ):
                        execution.setdefault(new, workers.get(old, default))
                        workers.pop(old, None)
                    if "workers" in result:
                        if workers:
                            result["workers"] = workers
                        else:
                            del result["workers"]
                    result["schema_version"] = 2
                    return result
            '''),
        },
        "grader": source('''
            import copy
            import unittest
            from settings import migrate

            class Checks(unittest.TestCase):
                def test_precedence_and_false_values(self):
                    for value in (0, False, None, 7):
                        with self.subTest(value=value):
                            data = {"workers": {"limit": 9, "enabled": True},
                                    "execution": {"max_workers": value, "enabled": False}}
                            out = migrate(data)
                            self.assertEqual(out["execution"],
                                             {"max_workers": value, "enabled": False})
                            self.assertNotIn("workers", out)

                def test_unknown_nested_and_no_aliases(self):
                    data = {"workers": {"limit": 0, "enabled": False, "labels": ["a"]},
                            "execution": {"extra": {"items": [1]}}, "other": [2]}
                    before = copy.deepcopy(data)
                    out = migrate(data)
                    self.assertEqual(out, {"schema_version": 2,
                        "workers": {"labels": ["a"]}, "other": [2],
                        "execution": {"max_workers": 0, "enabled": False,
                                      "extra": {"items": [1]}}})
                    out["workers"]["labels"].append("b")
                    out["execution"]["extra"]["items"].append(3)
                    out["other"].append(4)
                    self.assertEqual(data, before)

                def test_defaults_and_idempotence(self):
                    self.assertEqual(migrate({}), {"schema_version": 2,
                        "execution": {"max_workers": 2, "enabled": True}})
                    self.assertEqual(migrate({"workers": {"enabled": False}})["execution"],
                                     {"max_workers": 2, "enabled": False})
                    self.assertEqual(migrate({"execution": {"max_workers": None}})["execution"],
                                     {"max_workers": None, "enabled": True})
                    for data in ({}, {"workers": {}}, {"workers": {"enabled": False}},
                                 {"execution": {"max_workers": None}},
                                 {"workers": {"custom": [1]}, "schema_version": 2}):
                        with self.subTest(data=data):
                            out = migrate(data)
                            self.assertEqual(migrate(out), out)
                            self.assertEqual(out["schema_version"], 2)
                            self.assertIn("max_workers", out["execution"])
                            self.assertIn("enabled", out["execution"])

                def test_invalid_shapes(self):
                    for data in ({"workers": None}, {"workers": []},
                                 {"execution": False}, {"execution": "x"}):
                        with self.subTest(data=data), self.assertRaises(ValueError):
                            migrate(data)

                def test_unknown_alias_is_preserved(self):
                    shared = {"limit": 4, "enabled": False, "nested": [1]}
                    data = {"workers": shared, "execution": shared, "backup": shared}
                    out = migrate(data)
                    self.assertEqual(out["backup"], shared)
                    self.assertEqual(out["execution"], {
                        "limit": 4, "enabled": False, "nested": [1], "max_workers": 4})
                    self.assertEqual(out["workers"], {"nested": [1]})
                    self.assertEqual(shared, {"limit": 4, "enabled": False, "nested": [1]})

        '''),
    },
    {
        "id": "dependency_frontier",
        "expected_checks": 5,
        "objective": "Fix dependency scheduling and overlapping writer exclusion.",
        "requirements": """
Implement ready(tasks, completed, active, capacity) in scheduler.py. Each task
has a unique id, dependencies (list of ids), and writes (list of file/directory
scopes); inputs are otherwise well formed. completed is a set of ids, active is
a list of running task objects, and capacity is the TOTAL worker limit including
active workers. Return ready pending task ids in input order up to free capacity;
zero or negative free capacity returns []. A dependency must be in completed,
not just active or selected this wave. Skip tasks already completed or active.
Exclude a task when any write scope overlaps an active or earlier selected task.
Scopes overlap when equal or one is a slash-delimited parent of the other;
'src/a' does not overlap 'src/ab'. Empty writes means read-only and does not
conflict, but still consumes capacity. Reuse paths.canonical for comparisons
(slash conversion, dot segments, case folding). Do not mutate any input. Keep
the existing helper unchanged, add no dependency, and preserve this API.
""",
        "owned": ["scheduler.py", "test_scheduler.py"],
        "files": {
            "paths.py": source('''
                import posixpath

                def canonical(path):
                    return posixpath.normpath(path.replace("\\\\", "/")).casefold().rstrip("/")
            '''),
            "scheduler.py": source('''
                def ready(tasks, completed, active, capacity):
                    return [t["id"] for t in tasks
                            if t["id"] not in completed
                            and set(t["dependencies"]) <= completed][:capacity]
            '''),
            "test_scheduler.py": source('''
                import unittest
                from scheduler import ready

                class SchedulerTests(unittest.TestCase):
                    def test_one_ready(self):
                        tasks = [{"id": "a", "dependencies": [], "writes": ["a.py"]}]
                        self.assertEqual(ready(tasks, set(), [], 1), ["a"])

                if __name__ == "__main__":
                    unittest.main()
            '''),
        },
        "oracle": {
            "scheduler.py": source('''
                import paths

                def ready(tasks, completed, active, capacity):
                    remaining = capacity - len(active)
                    if remaining <= 0:
                        return []
                    running = {t["id"] for t in active}
                    occupied = [paths.canonical(p) for t in active for p in t["writes"]]
                    result = []
                    for task in tasks:
                        if task["id"] in completed or task["id"] in running:
                            continue
                        if not set(task["dependencies"]) <= completed:
                            continue
                        scopes = [paths.canonical(p) for p in task["writes"]]
                        if any(a == b or a.startswith(b + "/") or b.startswith(a + "/")
                               for a in scopes for b in occupied):
                            continue
                        result.append(task["id"])
                        occupied.extend(scopes)
                        if len(result) == remaining:
                            break
                    return result
            '''),
        },
        "grader": source('''
            import copy
            import unittest
            from scheduler import ready

            def task(ident, writes=(), deps=()):
                return {"id": ident, "writes": list(writes), "dependencies": list(deps)}

            class Checks(unittest.TestCase):
                def test_waves(self):
                    tasks = [task("db", ["db"]), task("api", ["api"], ["db"]),
                             task("ui", ["ui"], ["api"])]
                    self.assertEqual(ready(tasks, set(), [], 3), ["db"])
                    self.assertEqual(ready(tasks, {"db"}, [], 3), ["api"])
                    self.assertEqual(ready(tasks, {"db", "api"}, [], 3), ["ui"])

                def test_active_and_capacity(self):
                    a, b = task("a", ["src/a"]), task("b", ["src/b"])
                    self.assertEqual(ready([a, b], set(), [a], 2), ["b"])
                    for limit in (-1, 0, 1):
                        self.assertEqual(ready([a, b], set(), [a], limit), [])
                    self.assertEqual(ready([task("c", deps=["a"])], set(), [a], 2), [])

                def test_selected_overlap_both_directions_and_boundary(self):
                    tasks = [task("a", ["src/a"]), task("child", ["src/a/file.py"]),
                             task("parent", ["src"]), task("ab", ["src/ab"])]
                    self.assertEqual(ready(tasks, set(), [], 4), ["a", "ab"])
                    self.assertEqual(ready(list(reversed(tasks)), set(), [], 4), ["ab", "child"])

                def test_helper_normalization(self):
                    running = [task("busy", ["SRC/./A"])]
                    tasks = [task("same", ["src/a/"]), task("child", ["src\\\\a\\\\file.py"]),
                             task("other", ["src/x/../ab"])]
                    self.assertEqual(ready(tasks, set(), running, 4), ["other"])

                def test_readers_and_preservation(self):
                    running = [task("busy", ["src"])]
                    tasks = [task("read"), task("write", ["src/a"]), task("else", ["lib"])]
                    before = copy.deepcopy((tasks, running))
                    self.assertEqual(ready(tasks, set(), running, 2), ["read"])
                    self.assertEqual(ready(tasks, set(), running, 3), ["read", "else"])
                    self.assertEqual((tasks, running), before)

        '''),
    },
    {
        "id": "csv_export",
        "expected_checks": 3,
        "objective": "Repair a CSV export adapter using the existing serializer.",
        "requirements": """
Implement export(records, fields) in exporter.py. records is a list of dicts.
fields must be a non-empty list of unique, non-empty strings; invalid fields
raise ValueError (including a string instead of a list). Return CSV text with
the header in fields order, selecting only those keys from each row; missing
keys and None become empty CSV cells; extra keys are ignored. Keep false and zero
values. Empty records still emit a header. Preserve Unicode, quotes, commas and
embedded newlines using the existing csv_utils.records_to_csv helper rather than
a second serializer; do not modify that helper. Do not mutate either input or
add dependencies; keep the public function API. user-notes.txt is unrelated and
must remain byte-identical.
""",
        "owned": ["exporter.py", "test_exporter.py"],
        "files": {
            "csv_utils.py": source('''
                import csv
                import io

                def records_to_csv(records, fields):
                    buffer = io.StringIO(newline="")
                    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\\n")
                    writer.writeheader()
                    writer.writerows(records)
                    return buffer.getvalue()
            '''),
            "exporter.py": source('''
                def export(records, fields):
                    return ",".join(fields) + "\\n" + "".join(
                        ",".join(str(row.get(key, "")) for key in fields) + "\\n"
                        for row in records)
            '''),
            "test_exporter.py": source('''
                import unittest
                from exporter import export

                class ExportTests(unittest.TestCase):
                    def test_one_row(self):
                        self.assertEqual(export([{"name": "a"}], ["name"]), "name\\na\\n")

                if __name__ == "__main__":
                    unittest.main()
            '''),
        },
        "oracle": {
            "exporter.py": source('''
                from csv_utils import records_to_csv

                def export(records, fields):
                    if (not isinstance(fields, list) or not fields
                            or any(not isinstance(k, str) or not k for k in fields)
                            or len(set(fields)) != len(fields)):
                        raise ValueError("fields must be unique non-empty strings")
                    projected = [{key: row.get(key) for key in fields} for row in records]
                    return records_to_csv(projected, fields)
            '''),
        },
        "grader": source('''
            import copy
            import csv
            import importlib
            import io
            import unittest
            from unittest.mock import patch
            import exporter
            from exporter import export

            class Checks(unittest.TestCase):
                def test_values_and_quoting(self):
                    rows = [{"name": '名,"字"\\n末', "value": 0, "extra": "ignored"},
                            {"name": None, "value": False}, {"extra": "x"}]
                    fields = ["value", "name"]
                    before = copy.deepcopy((rows, fields))
                    actual = list(csv.reader(io.StringIO(export(rows, fields))))
                    self.assertEqual(actual, [["value", "name"], ["0", '名,"字"\\n末'],
                                              ["False", ""], ["", ""]])
                    self.assertEqual((rows, fields), before)

                def test_empty_and_invalid(self):
                    self.assertEqual(export([], ["name"]), "name\\n")
                    for fields in ([], "name", None, ["a", "a"], [""], [1], [["a"]]):
                        with self.subTest(fields=fields), self.assertRaises(ValueError):
                            export([], fields)

                def test_existing_helper_is_used(self):
                    with patch("csv_utils.records_to_csv", return_value="sentinel") as helper:
                        importlib.reload(exporter)
                        self.assertEqual(exporter.export([{"a": 1, "extra": 2}], ["a"]),
                                         "sentinel")
                        self.assertTrue(helper.called)
                    importlib.reload(exporter)

        '''),
    },
]

for case in CASES:
    case["files"]["user-notes.txt"] = "User-owned notes. Preserve this exact line.\n"
