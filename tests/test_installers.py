#!/usr/bin/env python3
"""Transactional installer lifecycle tests, including v1.0 -> four-tier migration."""

from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SKILL = Path(".agents/skills/codex-prove")
ALIAS = Path(".agents/skills/sol-control")
CONTROLLER = Path(".codex/agents/prove-controller.toml")
COMPLEX = Path(".codex/agents/prove-complex-worker.toml")
EFFICIENT = Path(".codex/agents/prove-efficient-worker.toml")
SPECIALIST = Path(".codex/agents/prove-specialist-worker.toml")
STATE = Path(".codex/codex-prove/install-state")
V100_TARGETS = (SKILL, ALIAS, CONTROLLER, COMPLEX, EFFICIENT)
CURRENT_TARGETS = (*V100_TARGETS, SPECIALIST)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(root: Path) -> str:
    rows: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append(f"L\t{relative}\t{os.readlink(path)}\n")
        elif path.is_dir():
            rows.append(f"D\t{relative}\n")
        elif path.is_file():
            rows.append(f"F\t{relative}\t{file_hash(path)}\n")
        else:
            rows.append(f"O\t{relative}\n")
    return hashlib.sha256("".join(rows).encode()).hexdigest()


def snapshot(root: Path) -> dict[str, tuple[str, bytes | str | None]]:
    result: dict[str, tuple[str, bytes | str | None]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("link", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("dir", None)
        elif path.is_file():
            result[relative] = ("file", path.read_bytes())
    return result


class PosixInstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX lifecycle runs on macOS/Linux; Windows uses windows-lifecycle.ps1")
        self.temporary = tempfile.TemporaryDirectory(prefix="codex-prove-v1.")
        self.home = Path(self.temporary.name) / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def path(self, relative: Path) -> Path:
        return self.home / relative

    def run_script(self, script: str, *args: str, failpoint: str | None = None, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["ORCHESTRATE_HOME"] = str(self.home)
        env.pop("ORCHESTRATE_FAILPOINT", None)
        if failpoint:
            env["ORCHESTRATE_FAILPOINT"] = failpoint
        env.update(extra_env or {})
        return subprocess.run(
            ["bash", str(SCRIPTS / script), *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def assert_current(self) -> None:
        for relative in CURRENT_TARGETS:
            self.assertTrue(self.path(relative).exists(), relative)
        state = self.path(STATE).read_text(encoding="utf-8")
        self.assertIn("version=6", state)
        self.assertIn("skill_sha256=", state)
        self.assertIn("compat_skill_sha256=", state)
        self.assertIn("controller_sha256=", state)
        self.assertIn(f"specialist_worker_sha256={file_hash(self.path(SPECIALIST))}", state)
        for relative in (CONTROLLER, COMPLEX, EFFICIENT, SPECIALIST):
            self.assertEqual((ROOT / relative).read_bytes(), self.path(relative).read_bytes())

    def install(self) -> subprocess.CompletedProcess[str]:
        result = self.run_script("install.sh")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assert_current()
        return result

    def make_v050_install(self) -> dict[str, bytes]:
        old_skill = self.home / ".agents/skills/sol-control"
        old_agents = self.home / ".codex/agents"
        old_skill.mkdir(parents=True)
        old_agents.mkdir(parents=True)
        (old_skill / "SKILL.md").write_text(
            "---\nname: sol-control\ndescription: managed v0.5 fixture\n---\nold\n",
            encoding="utf-8",
        )
        files = {
            "sol-controller.toml": b'name = "sol-controller"\nmodel = "gpt-5.6-sol"\n',
            "terra-high-worker.toml": b'name = "terra-high-worker"\nmodel = "gpt-5.6-terra"\n',
            "luna-max-worker.toml": b'name = "luna-max-worker"\nmodel = "gpt-5.6-luna"\n',
        }
        for name, content in files.items():
            (old_agents / name).write_bytes(content)
        old_state = self.home / ".codex/sol-control/install-state"
        old_state.parent.mkdir(parents=True)
        old_state.write_text(
            "\n".join(
                (
                    "version=4",
                    "backup_id=v050-fixture",
                    f"skill_sha256={tree_hash(old_skill)}",
                    f"sol_sha256={file_hash(old_agents / 'sol-controller.toml')}",
                    f"terra_sha256={file_hash(old_agents / 'terra-high-worker.toml')}",
                    f"luna_sha256={file_hash(old_agents / 'luna-max-worker.toml')}",
                    "",
                )
            ),
            encoding="utf-8",
        )
        return {str(path.relative_to(self.home)): path.read_bytes() for path in old_agents.glob("*.toml")}

    def test_install_creates_v1_targets_and_state(self) -> None:
        result = self.install()
        self.assertIn(str(self.path(SKILL)), result.stdout)
        self.assertIn("Backup path:", result.stdout)
        self.assertIn("name: codex-prove", (self.path(SKILL) / "SKILL.md").read_text())
        self.assertIn("$codex-prove", (self.path(ALIAS) / "SKILL.md").read_text())

    def make_v100_install(self) -> dict[str, bytes]:
        for relative in (SKILL, ALIAS):
            self.path(relative).mkdir(parents=True)
            (self.path(relative) / "SKILL.md").write_text(f"old {relative.name}\n")
        for relative, model in ((CONTROLLER, "gpt-5.6-sol"), (COMPLEX, "gpt-5.6-terra"), (EFFICIENT, "gpt-5.6-luna")):
            self.path(relative).parent.mkdir(parents=True, exist_ok=True)
            self.path(relative).write_text(f'name = "{relative.stem}"\nmodel = "{model}"\n')
        self.path(STATE).parent.mkdir(parents=True)
        fields = {
            "version": "5", "backup_id": "v100-fixture",
            "skill_sha256": tree_hash(self.path(SKILL)),
            "compat_skill_sha256": tree_hash(self.path(ALIAS)),
            "controller_sha256": file_hash(self.path(CONTROLLER)),
            "complex_worker_sha256": file_hash(self.path(COMPLEX)),
            "efficient_worker_sha256": file_hash(self.path(EFFICIENT)),
        }
        self.path(STATE).write_text("".join(f"{key}={value}\n" for key, value in fields.items()))
        # Original v1.0 backup format, representing the preceding empty install.
        relatives = [
            SKILL, ALIAS, Path(".agents/skills/sol-luna"), Path(".agents/skills/orchestrate-sol-luna"),
            CONTROLLER, COMPLEX, EFFICIENT, Path(".codex/agents/sol-controller.toml"),
            Path(".codex/agents/terra-high-worker.toml"), Path(".codex/agents/luna-max-worker.toml"),
            Path(".codex/agents/sol-planner.toml"), STATE, Path(".codex/sol-control/install-state"),
            Path(".codex/sol-luna/install-state"), Path(".codex/orchestrate-sol-luna/install-state"),
        ]
        backup = self.path(STATE).parent / "backups/v100-fixture"
        (backup / "entries").mkdir(parents=True)
        rows = ["version=5", "entry_count=15"]
        for number, relative in enumerate(relatives, 1):
            rows.extend((f"entry_{number}_path={relative.as_posix()}", f"entry_{number}_kind={'directory' if number <= 4 else 'file'}", f"entry_{number}_presence=absent", f"entry_{number}_sha256="))
        (backup / "manifest").write_text("\n".join(rows) + "\n")
        return {str(path.relative_to(self.home)): path.read_bytes() for path in self.home.rglob("*") if path.is_file()}

    def test_v100_upgrade_restore_and_original_backup_round_trip(self) -> None:
        old = self.make_v100_install()
        self.install()
        restored = self.run_script("uninstall.sh", "--restore-latest")
        self.assertEqual(0, restored.returncode, restored.stdout)
        for relative, content in old.items():
            self.assertEqual(content, (self.home / relative).read_bytes(), relative)
        self.assertFalse(self.path(SPECIALIST).exists())
        original = self.run_script("uninstall.sh", "--restore-latest")
        self.assertEqual(0, original.returncode, original.stdout)
        for relative in (*CURRENT_TARGETS, STATE):
            self.assertFalse(self.path(relative).exists(), relative)

    def test_v100_upgrade_failure_restores_every_old_file(self) -> None:
        old = self.make_v100_install()
        result = self.run_script("install.sh", failpoint="after-state")
        self.assertNotEqual(0, result.returncode, result.stdout)
        for relative, content in old.items():
            self.assertEqual(content, (self.home / relative).read_bytes(), relative)
        self.assertFalse(self.path(SPECIALIST).exists())

    def test_unowned_specialist_is_never_overwritten_or_removed(self) -> None:
        self.make_v100_install()
        self.path(SPECIALIST).write_text("user-owned Sol profile\n")
        before = snapshot(self.home)
        install = self.run_script("install.sh")
        self.assertNotEqual(0, install.returncode, install.stdout)
        self.assertEqual(before, snapshot(self.home))
        failed = self.run_script("uninstall.sh", failpoint="after-remove")
        self.assertNotEqual(0, failed.returncode, failed.stdout)
        self.assertEqual(before, snapshot(self.home))
        uninstalled = self.run_script("uninstall.sh")
        self.assertEqual(0, uninstalled.returncode, uninstalled.stdout)
        self.assertEqual("user-owned Sol profile\n", self.path(SPECIALIST).read_text())

    def test_modified_specialist_blocks_install_and_uninstall_without_mutation(self) -> None:
        self.install()
        self.path(SPECIALIST).write_text("user change\n")
        before = snapshot(self.home)
        for script in ("install.sh", "uninstall.sh"):
            result = self.run_script(script)
            self.assertNotEqual(0, result.returncode, result.stdout)
            self.assertEqual(before, snapshot(self.home))

    def test_corrupt_backup_does_not_remove_current_files(self) -> None:
        self.install()
        self.install()
        fields = dict(line.split("=", 1) for line in self.path(STATE).read_text().splitlines())
        manifest = self.path(STATE).parent / "backups" / fields["backup_id"] / "manifest"
        manifest.write_text(manifest.read_text().replace("entry_1_path=.agents/skills/codex-prove", "entry_1_path=../unsafe"))
        before = snapshot(self.home)
        result = self.run_script("uninstall.sh", "--restore-latest")
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertEqual(before, snapshot(self.home))

    def test_check_mode_is_read_only_for_fresh_and_current_home(self) -> None:
        before = snapshot(Path(self.temporary.name))
        check = self.run_script("install.sh", "--check")
        self.assertEqual(0, check.returncode, check.stdout)
        self.assertEqual(before, snapshot(Path(self.temporary.name)))

        self.install()
        before = snapshot(self.home)
        check = self.run_script("install.sh", "--check")
        self.assertEqual(0, check.returncode, check.stdout)
        self.assertEqual(before, snapshot(self.home))

    def test_unowned_collision_and_modified_install_fail_closed(self) -> None:
        collision = self.path(SKILL)
        collision.mkdir(parents=True)
        (collision / "user.txt").write_text("keep", encoding="utf-8")
        before = snapshot(self.home)
        result = self.run_script("install.sh")
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("no matching ownership state", result.stdout)
        self.assertEqual(before, snapshot(self.home))

        for path in sorted(collision.rglob("*"), reverse=True):
            path.unlink()
        collision.rmdir()
        self.install()
        (self.path(SKILL) / "SKILL.md").write_text("user modification\n", encoding="utf-8")
        before = snapshot(self.home)
        result = self.run_script("install.sh")
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("modified", result.stdout)
        self.assertEqual(before, snapshot(self.home))

    def test_failpoint_rolls_back_current_install(self) -> None:
        self.install()
        before = {str(relative): snapshot(self.path(relative)) for relative in CURRENT_TARGETS}
        before_state = self.path(STATE).read_bytes()
        backup_root = self.home / ".codex/codex-prove/backups"
        before_backups = {path.name for path in backup_root.iterdir()}
        result = self.run_script("install.sh", failpoint="after-replace")
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertEqual(before, {str(relative): snapshot(self.path(relative)) for relative in CURRENT_TARGETS})
        self.assertEqual(before_state, self.path(STATE).read_bytes())
        after_backups = {path.name for path in backup_root.iterdir()}
        self.assertEqual(1, len(after_backups - before_backups))

    def assert_failed_recovery_is_preserved(self, script: str, *, evacuation: bool = False) -> None:
        self.install()
        if script == "uninstall.sh" and evacuation:
            self.install()  # --restore-latest places a prior version at the target.
        original = self.path(SPECIALIST).read_bytes()
        install = script == "install.sh"
        prefix = ".transaction." if install else ".uninstall."
        held = "old" if install else "current"
        tool_dir = Path(self.temporary.name) / "fault-bin"
        tool_dir.mkdir()
        real_mv = shutil.which("mv")
        self.assertIsNotNone(real_mv)
        pattern = f"*/{prefix}*/failed/15/current" if evacuation else f"*/{prefix}*/{held}/15"
        argument = "$2" if evacuation else "$1"
        wrapper = tool_dir / "mv"
        wrapper.write_text(
            f'#!/bin/sh\ncase "{argument}" in\n  {pattern}) exit 73 ;;\nesac\n'
            f'exec {shlex.quote(real_mv)} "$@"\n'
        )
        wrapper.chmod(0o755)
        args = ("--restore-latest",) if script == "uninstall.sh" and evacuation else ()
        result = self.run_script(
            script, *args, failpoint="after-state" if install else "after-remove",
            extra_env={"PATH": f"{tool_dir}{os.pathsep}{os.environ['PATH']}"},
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        transactions = list(self.path(STATE).parent.glob(f"{prefix}*"))
        self.assertEqual(1, len(transactions), "failed recovery deleted its transaction copy")
        transaction = transactions[0]
        self.assertEqual(original, (transaction / held / "15").read_bytes())
        self.assertIn(f"Recovery path: {transaction.resolve()}", result.stdout)
        if evacuation:
            self.assertEqual(original, self.path(SPECIALIST).read_bytes())
        else:
            self.assertFalse(self.path(SPECIALIST).exists())
        # A single failed path must not prevent recovery of other managed files.
        self.assertEqual((ROOT / CONTROLLER).read_bytes(), self.path(CONTROLLER).read_bytes())
        self.assertTrue(self.path(STATE).is_file())

    def test_install_failed_restore_preserves_recovery_copy(self) -> None:
        self.assert_failed_recovery_is_preserved("install.sh")

    def test_uninstall_failed_restore_preserves_recovery_copy(self) -> None:
        self.assert_failed_recovery_is_preserved("uninstall.sh")

    def test_install_failed_evacuation_does_not_overwrite_target(self) -> None:
        self.assert_failed_recovery_is_preserved("install.sh", evacuation=True)

    def test_uninstall_failed_evacuation_does_not_overwrite_target(self) -> None:
        self.assert_failed_recovery_is_preserved("uninstall.sh", evacuation=True)

    def assert_interrupt_after_move_recovers_original(self, script: str) -> None:
        self.install()
        before_state = self.path(STATE).read_bytes()
        prefix, held = (".transaction.", "old") if script == "install.sh" else (".uninstall.", "current")
        tool_dir = Path(self.temporary.name) / "signal-bin"
        tool_dir.mkdir()
        real_mv = shutil.which("mv")
        self.assertIsNotNone(real_mv)
        wrapper = tool_dir / "mv"
        # Signal only this wrapper's immediate test-script parent, after a real move.
        wrapper.write_text(
            f'#!/bin/sh\n{shlex.quote(real_mv)} "$@"\nmove_status=$?\n'
            f'case "$2" in */{prefix}*/{held}/15)\n'
            '  if [ "$move_status" -eq 0 ]; then kill -TERM "$PPID"; fi ;;\nesac\n'
            'exit "$move_status"\n'
        )
        wrapper.chmod(0o755)
        result = self.run_script(script, extra_env={"PATH": f"{tool_dir}{os.pathsep}{os.environ['PATH']}"})
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assert_current()
        self.assertEqual(before_state, self.path(STATE).read_bytes())

    def test_install_interrupted_after_move_restores_unmarked_original(self) -> None:
        self.assert_interrupt_after_move_recovers_original("install.sh")

    def test_uninstall_interrupted_after_move_restores_unmarked_original(self) -> None:
        self.assert_interrupt_after_move_recovers_original("uninstall.sh")

    def assert_partial_cleanup_keeps_committed_result(self, script: str) -> None:
        self.install()
        prefix, held = (".transaction.", "old") if script == "install.sh" else (".uninstall.", "current")
        tool_dir = Path(self.temporary.name) / "cleanup-bin"
        tool_dir.mkdir()
        real_rm = shutil.which("rm")
        self.assertIsNotNone(real_rm)
        wrapper = tool_dir / "rm"
        # Delete one recovery file, then emulate failed post-commit garbage collection.
        wrapper.write_text(
            f'#!/bin/sh\ncase "$2" in */{prefix}*)\n'
            f'  {shlex.quote(real_rm)} -f "$2/{held}/11"\n  exit 73 ;;\nesac\n'
            f'exec {shlex.quote(real_rm)} "$@"\n'
        )
        wrapper.chmod(0o755)
        result = self.run_script(script, extra_env={"PATH": f"{tool_dir}{os.pathsep}{os.environ['PATH']}"})
        self.assertNotEqual(0, result.returncode, result.stdout)
        if script == "install.sh":
            self.assert_current()
        else:
            for relative in (*CURRENT_TARGETS, STATE):
                self.assertFalse(self.path(relative).exists(), relative)
        transactions = list(self.path(STATE).parent.glob(f"{prefix}*"))
        self.assertEqual(1, len(transactions))
        self.assertIn("committed", result.stdout)
        self.assertIn(f"Recovery path: {transactions[0].resolve()}", result.stdout)

    def test_install_cleanup_failure_does_not_roll_back_committed_files(self) -> None:
        self.assert_partial_cleanup_keeps_committed_result("install.sh")

    def test_uninstall_cleanup_failure_does_not_restore_partially_deleted_files(self) -> None:
        self.assert_partial_cleanup_keeps_committed_result("uninstall.sh")

    def test_uninstall_removes_only_owned_v1_targets(self) -> None:
        unrelated = self.home / ".codex/agents/user-agent.toml"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("user", encoding="utf-8")
        self.install()
        result = self.run_script("uninstall.sh")
        self.assertEqual(0, result.returncode, result.stdout)
        for relative in CURRENT_TARGETS:
            self.assertFalse(self.path(relative).exists(), relative)
        self.assertFalse(self.path(STATE).exists())
        self.assertEqual("user", unrelated.read_text())

    def test_uninstall_rejects_linked_managed_parents_without_mutation(self) -> None:
        root = Path(self.temporary.name)
        for index, relative in enumerate((".agents", ".agents/skills", ".codex",
                                          ".codex/agents", ".codex/codex-prove")):
            with self.subTest(parent=relative):
                self.home = root / f"linked-parent-{index}"
                self.install()
                parent = self.home / relative
                external = root / f"external-{index}"
                parent.rename(external)
                parent.symlink_to(external, target_is_directory=True)
                before = snapshot(root)
                result = self.run_script("uninstall.sh")
                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertEqual(before, snapshot(root))

    def test_linked_legacy_state_parent_blocks_migration_without_mutation(self) -> None:
        self.make_v050_install()
        root = Path(self.temporary.name)
        parent = self.home / ".codex/sol-control"
        external = root / "external-legacy-state"
        parent.rename(external)
        parent.symlink_to(external, target_is_directory=True)
        before = snapshot(root)
        for arguments in (("--check",), ()):
            with self.subTest(arguments=arguments):
                result = self.run_script("install.sh", *arguments)
                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertEqual(before, snapshot(root))

    def test_restore_rejects_linked_backup_parent_without_mutation(self) -> None:
        self.install()
        self.install()
        root = Path(self.temporary.name)
        parent = self.home / ".codex/codex-prove/backups"
        external = root / "external-backups"
        parent.rename(external)
        parent.symlink_to(external, target_is_directory=True)
        before = snapshot(root)
        result = self.run_script("uninstall.sh", "--restore-latest")
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertEqual(before, snapshot(root))

    def test_v050_upgrade_and_restore_latest_round_trip(self) -> None:
        old_agent_bytes = self.make_v050_install()
        self.install()
        self.assertFalse((self.home / ".codex/sol-control/install-state").exists())
        self.assertFalse((self.home / ".codex/agents/sol-controller.toml").exists())
        result = self.run_script("uninstall.sh", "--restore-latest")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertFalse(self.path(SKILL).exists())
        self.assertTrue((self.home / ".agents/skills/sol-control/SKILL.md").is_file())
        self.assertTrue((self.home / ".codex/sol-control/install-state").is_file())
        for relative, expected in old_agent_bytes.items():
            self.assertEqual(expected, (self.home / relative).read_bytes())


class ScriptSurfaceTests(unittest.TestCase):
    def test_native_windows_scripts_keep_ps51_safety_and_rollback_markers(self) -> None:
        install = (SCRIPTS / "install.ps1").read_text(encoding="utf-8")
        uninstall = (SCRIPTS / "uninstall.ps1").read_text(encoding="utf-8")
        validate = (SCRIPTS / "validate.ps1").read_text(encoding="utf-8")
        lifecycle = (ROOT / "tests/windows-lifecycle.ps1").read_text(encoding="utf-8")
        for marker in (
            "codex-prove",
            "prove-controller.toml",
            "prove-complex-worker.toml",
            "prove-efficient-worker.toml",
            "prove-specialist-worker.toml",
            "install-state",
            "SHA256",
            "-LiteralPath",
        ):
            self.assertIn(marker, install)
            self.assertIn(marker, uninstall + validate + lifecycle)
        self.assertIn("#requires -Version 5.1", install)
        self.assertIn("ORCHESTRATE_FAILPOINT", install)
        self.assertIn("RestoreLatest", uninstall)
        self.assertIn("v050", lifecycle)


if __name__ == "__main__":
    unittest.main(verbosity=2)
