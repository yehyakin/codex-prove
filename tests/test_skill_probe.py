#!/usr/bin/env python3
"""The optional live probe must reject unsafe requests before launching Codex."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_skill_probe


ROOT = Path(__file__).resolve().parents[1]


class SkillProbeGuards(unittest.TestCase):
    def test_source_workspace_is_rejected_before_model_launch(self):
        run = subprocess.run([
            sys.executable, '-B', str(ROOT / 'tests/run_skill_probe.py'),
            '--run-model', '--workspace', str(ROOT), '--prompt-file', '/not-read',
            '--output', '/not-created', '--codex', '/must-not-launch',
        ], text=True, capture_output=True)
        self.assertEqual(2, run.returncode)
        self.assertIn('disposable Git workspace', run.stderr)
        self.assertNotIn('Traceback', run.stderr)

    def test_model_call_requires_explicit_opt_in(self):
        run = subprocess.run([
            sys.executable, '-B', str(ROOT / 'tests/run_skill_probe.py'),
            '--workspace', str(ROOT), '--prompt-file', '/not-read',
            '--output', '/not-created', '--codex', '/must-not-launch',
        ], text=True, capture_output=True)
        self.assertEqual(2, run.returncode)
        self.assertIn('require --run-model', run.stderr)

    def test_existing_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='probe-guard.') as temporary:
            workspace = Path(temporary) / 'workspace'
            (workspace / '.git').mkdir(parents=True)
            output = Path(temporary) / 'existing'
            output.mkdir()
            sentinel = output / 'keep.txt'
            sentinel.write_text('unchanged\n')
            run = subprocess.run([
                sys.executable, '-B', str(ROOT / 'tests/run_skill_probe.py'),
                '--run-model', '--workspace', str(workspace), '--prompt-file', '/not-read',
                '--output', str(output), '--codex', '/must-not-launch',
            ], text=True, capture_output=True)
            self.assertEqual(2, run.returncode)
            self.assertIn('new output directory', run.stderr)
            self.assertEqual('unchanged\n', sentinel.read_text())

    def test_windows_cannot_start_without_supported_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='probe-guard.') as temporary:
            workspace = Path(temporary) / 'workspace'
            (workspace / '.git').mkdir(parents=True)
            argv = ['probe', '--run-model', '--workspace', str(workspace),
                    '--prompt-file', '/not-read', '--output', str(Path(temporary) / 'new'),
                    '--codex', '/must-not-launch']
            with patch.object(sys, 'argv', argv), patch.object(sys, 'platform', 'win32'), \
                    patch('run_skill_probe.shutil.which', return_value=None), \
                    patch('argparse.ArgumentParser.error', side_effect=ValueError) as error:
                with self.assertRaises(ValueError):
                    run_skill_probe.main()
            self.assertIn('POSIX process-group cleanup', error.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
