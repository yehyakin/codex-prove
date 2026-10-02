#!/usr/bin/env python3
"""The optional live probe must reject unsafe requests before launching Codex."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_skill_probe


ROOT = Path(__file__).resolve().parents[1]


class SkillProbeGuards(unittest.TestCase):
    def test_host_selection_does_not_claim_observed_or_child_identity(self):
        task = "$codex-prove: 修复本地夹具；保留所有验收。\n"
        for model, effort in (("gpt-6.1-sol", "high"), ("gpt-6-sol", "medium")):
            with self.subTest(model=model, effort=effort):
                selection, prompt = run_skill_probe.prepare_prompt(task, model, effort)
                self.assertEqual(model, selection["selected_model"])
                self.assertEqual(effort, selection["selected_reasoning_effort"])
                self.assertEqual("current_host_only", selection["scope"])
                self.assertIsNone(selection["observed_model"])
                self.assertIsNone(selection["observed_reasoning_effort"])
                self.assertEqual(selection, json.loads(prompt.splitlines()[1]))
                self.assertEqual(task, prompt.split("\n\n", 1)[1])

    def test_launcher_context_is_symmetric_for_baseline_and_skill_arm(self):
        task = "Repair the fixture and its regressions.\n"
        baseline = run_skill_probe.prepare_prompt(task, "gpt-6.1-sol", "high")
        candidate = run_skill_probe.prepare_prompt("$codex-prove\n" + task, "gpt-6.1-sol", "high")
        self.assertEqual(baseline[0], candidate[0])
        self.assertEqual(baseline[1].split("\n\n", 1)[0], candidate[1].split("\n\n", 1)[0])
        self.assertEqual("$codex-prove\n" + task, candidate[1].split("\n\n", 1)[1])

    def test_agent_limit_is_bounded_before_model_launch(self):
        for value in ("0", "9"):
            run = subprocess.run([
                sys.executable, '-B', str(ROOT / 'tests/run_skill_probe.py'),
                '--run-model', '--workspace', str(ROOT), '--prompt-file', '/not-read',
                '--output', '/not-created', '--codex', '/must-not-launch',
                '--max-agent-threads', value,
            ], text=True, capture_output=True)
            self.assertEqual(2, run.returncode)
            self.assertIn('max-agent-threads must be 1..8', run.stderr)

    def test_retained_transcript_and_capacity_are_explicit_local_options(self):
        for retained in (False, True):
            with tempfile.TemporaryDirectory(prefix='probe-command.') as temporary:
                workspace = Path(temporary) / 'workspace'
                (workspace / '.git').mkdir(parents=True)
                prompt = Path(temporary) / 'request.txt'
                ending = '\r\n' if retained else '\n'
                prompt.write_bytes(('Do the bounded fixture task. 保留验收。' + ending).encode('utf-8'))
                argv = ['probe', '--run-model', '--workspace', str(workspace),
                        '--prompt-file', str(prompt), '--output', str(Path(temporary) / 'result'),
                        '--codex', '/must-not-launch', '--max-agent-threads', '5']
                if retained:
                    argv.append('--retain-session')
                process_result = {'exit_code': 0, 'timed_out': False, 'elapsed_seconds': 0.01}
                with patch.object(sys, 'argv', argv), \
                        patch('run_skill_probe.shutil.which', return_value=None), \
                        patch('run_skill_probe.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'test-version\n')), \
                        patch('run_skill_probe.run_process', return_value=process_result) as run, \
                        patch('run_skill_probe.parse_usage', return_value={}) as usage, \
                        patch('builtins.print'), patch.object(sys, 'platform', 'darwin'):
                    with self.assertRaises(SystemExit) as completed:
                        run_skill_probe.main()
                self.assertEqual(0, completed.exception.code)
                command = run.call_args.args[0]
                self.assertEqual(not retained, '--ephemeral' in command)
                self.assertIn('agents.max_concurrent_threads_per_session=5', command)
                self.assertIn('--ignore-user-config', command)
                self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', command)
                self.assertEqual(1, run.call_count)
                self.assertEqual({'process_complete': True}, usage.call_args.kwargs)
                sent_prompt = run.call_args.args[2]
                output = Path(temporary) / 'result'
                invocation = json.loads((output / 'invocation.json').read_text())
                selection = invocation['host_selection']
                self.assertEqual(command[command.index('--model') + 1], selection['selected_model'])
                self.assertIn('model_reasoning_effort=' + json.dumps(selection['selected_reasoning_effort']), command)
                self.assertIsNone(selection['observed_model'])
                self.assertIsNone(selection['observed_reasoning_effort'])
                self.assertEqual(selection, json.loads(sent_prompt.splitlines()[1]))
                self.assertEqual(sent_prompt.encode('utf-8'), (output / 'prompt.txt').read_bytes())
                self.assertEqual(prompt.read_bytes(), (output / 'task-prompt.txt').read_bytes())
                self.assertEqual(hashlib.sha256(sent_prompt.encode()).hexdigest(), invocation['prompt_sha256'])
                self.assertEqual(hashlib.sha256(prompt.read_bytes()).hexdigest(), invocation['task_prompt_sha256'])
                self.assertNotEqual(invocation['prompt_sha256'], invocation['task_prompt_sha256'])

    def test_timeout_keeps_successful_usage_partial_in_the_saved_result(self):
        with tempfile.TemporaryDirectory(prefix='probe-timeout.') as temporary:
            root = Path(temporary)
            workspace = root / 'workspace'
            (workspace / '.git').mkdir(parents=True)
            prompt = root / 'request.txt'
            prompt.write_text('Inspect only this fixture.\n')
            output = root / 'result'
            argv = ['probe', '--run-model', '--workspace', str(workspace),
                    '--prompt-file', str(prompt), '--output', str(output), '--codex', '/must-not-launch']

            def fake_process(command, cwd, task_prompt, timeout, stdout_path, stderr_path):
                stdout_path.write_text(json.dumps({'type': 'turn.completed', 'usage': {
                    'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 10}}) + '\n')
                return {'exit_code': -9, 'timed_out': True, 'elapsed_seconds': 1.0}

            with patch.object(sys, 'argv', argv), patch.object(sys, 'platform', 'darwin'), \
                    patch('run_skill_probe.shutil.which', return_value=None), \
                    patch('run_skill_probe.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'test-version\n')), \
                    patch('run_skill_probe.run_process', side_effect=fake_process), patch('builtins.print'):
                with self.assertRaises(SystemExit) as completed:
                    run_skill_probe.main()
            self.assertEqual(1, completed.exception.code)
            result = json.loads((output / 'result.json').read_text())
            self.assertIsNone(result['usage'])
            self.assertIsNone(result['whole_run_usage'])
            self.assertEqual(100, result['observed_completed_usage']['input_tokens'])
            self.assertIn('process_incomplete', result['usage_issues'])

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
