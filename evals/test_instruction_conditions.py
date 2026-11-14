"""Native input and filesystem boundaries for standalone/baseline trials."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import run


class InstructionConditions(unittest.TestCase):
    def exercise(self, root, case, condition):
        auth = root / 'auth'
        auth.mkdir()
        (auth / 'auth.json').write_text('{}')
        args = argparse.Namespace(model='test', effort='low', timeout=1,
                                  auth_home=auth, condition=condition)
        host = Mock()
        host.events = []
        host.process.pid = 999999
        host.process.poll.return_value = 0
        replies = [{}, {'thread': {'id': 'first'}}]
        completions = []
        for i, _ in enumerate(case['turns']):
            if i == case.get('fresh_thread_before'):
                replies.append({'thread': {'id': 'recovered'}})
            replies.append({'turn': {'id': str(i)}})
            completions.append({'params': {'turn': {'id': str(i), 'status': 'completed'}}})
        host.request.side_effect = replies
        host.wait.side_effect = completions
        with patch('run.Host', return_value=host), patch('run.subprocess.check_output', return_value='test\n'), contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(run.trial(case, args, root / 'output'))
        return root / 'output', host

    def test_standalone_satchel_has_no_atlas_or_sibling_and_no_grader(self):
        case = {'id': 'editor', 'package': 'satchel', 'entry': 'to-eval',
                'fixture': 'eval-design-editor', 'check': 'unchanged', 'turns': ['Design the eval']}
        with tempfile.TemporaryDirectory() as d:
            output, host = self.exercise(Path(d), case, 'guided')
            skills = output / 'workspace/.agents/skills'
            self.assertEqual([p.name for p in skills.iterdir()], ['to-eval'])
            self.assertTrue((skills / 'to-eval/LICENSE').is_file())
            self.assertEqual((skills / 'to-eval/SKILL.md').read_bytes(),
                             (run.ROOT / 'plugins/satchel/skills/to-eval/SKILL.md').read_bytes())
            files = set(run.snapshot(output / 'workspace'))
            self.assertIn('sample.md', files)
            self.assertFalse(any('evaluation-authoring-review' in name or name.startswith('evals/') for name in files))
            calls = [c for c in host.request.call_args_list if c.args[0] == 'turn/start']
            self.assertEqual(calls[0].args[1]['input'][0],
                             {'type': 'skill', 'name': 'to-eval', 'path': str(skills / 'to-eval/SKILL.md')})
            metadata = json.loads((output / 'metadata.json').read_text())
            self.assertEqual(metadata['instruction_plan']['installed_skills'], ['to-eval'])
            self.assertIn('SKILL.md', metadata['candidate_files'])
            self.assertIn('to-eval/SKILL.md', metadata['staged_skill_files'])

    def test_unguided_preserves_fixture_without_skills_even_after_recovery(self):
        case = {'id': 'baseline', 'package': 'satchel', 'entry': 'unslop',
                'fixture': 'satchel-edit-scope', 'check': 'unchanged',
                'turns': ['Edit the draft', 'Continue from the file'], 'fresh_thread_before': 1,
                'git_root': True}
        with tempfile.TemporaryDirectory() as d:
            output, host = self.exercise(Path(d), case, 'unguided')
            self.assertFalse((output / 'workspace/.agents').exists())
            self.assertEqual((output / 'workspace/draft.md').read_text(),
                             run.FIXTURES['satchel-edit-scope']['draft.md'])
            turns = [c for c in host.request.call_args_list if c.args[0] == 'turn/start']
            for call, prompt in zip(turns, case['turns']):
                self.assertEqual(call.args[1]['input'], [{'type': 'text', 'text': prompt}])
            self.assertEqual(turns[1].args[1]['threadId'], 'recovered')
            meta = json.loads((output / 'metadata.json').read_text())
            self.assertEqual(meta['staged_skill_files'], {})
            self.assertTrue(meta['candidate_files'])  # identifies the withheld treatment source
            self.assertTrue(json.loads((output / 'result.json').read_text())['cleanup']['temporary_home_removed'])
            result = json.loads((output / 'result.json').read_text())
            self.assertEqual(result['condition'], 'unguided')
            self.assertEqual(result['routing_verdict'], 'NOT_APPLICABLE')
            self.assertFalse(result['tool_capture']['parsed_without_errors'])
            self.assertTrue((output / 'workspace/.git').is_dir())

    def test_preview_has_no_authentication_execution_or_output_side_effect(self):
        args = ['run.py', '--case', 'to-eval-editor', '--condition', 'unguided', '--preview']
        stdout = io.StringIO()
        with patch('sys.argv', args), patch('run.Host') as host, patch('run.trial') as trial, contextlib.redirect_stdout(stdout):
            run.main()
        plan = json.loads(stdout.getvalue())[0]
        self.assertEqual(plan['visible_fixture_files'], ['BRIEF.md', 'sample.md'])
        self.assertEqual(plan['installed_skills'], [])
        host.assert_not_called()
        trial.assert_not_called()

    def test_invalid_sources_and_fixtures_fail_before_creating_output(self):
        for change in ({'package': '../satchel'}, {'entry': '../atlas'},
                       {'package': 'satchel'}, {'fixture': 'not-registered'},
                       {'package': 'satchel', 'entry': 'to-eval', 'missing': True},
                       {'missing': True}, {'git_root': 'false'}):
            case = {'id': 'bad', 'check': 'unchanged', 'turns': ['Hello'], **change}
            with self.subTest(change=change), tempfile.TemporaryDirectory() as d:
                output = Path(d) / 'output'
                with self.assertRaises(ValueError):
                    run.trial(case, argparse.Namespace(condition='guided'), output)
                self.assertFalse(output.exists())

    def test_legacy_ledger_keeps_its_repository_free_setup(self):
        cases = json.loads((run.ROOT / 'evals/cases.json').read_text())
        case = next(c for c in cases if c['check'] == 'ledger')
        for condition in ('guided', 'unguided'):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as d:
                output, _ = self.exercise(Path(d), case, condition)
                self.assertFalse((output / 'workspace/.git').exists())
                metadata = json.loads((output / 'metadata.json').read_text())
                self.assertFalse(metadata['instruction_plan']['git_root'])

    def test_missing_lead_preview_matches_intended_staging(self):
        plan = run.preview({'id': 'missing', 'entry': 'atlas-handoff', 'check': 'unchanged', 'missing': True, 'turns': ['Hello']}, 'guided')
        self.assertNotIn('atlas', plan['installed_skills'])
        self.assertIn('atlas-handoff', plan['installed_skills'])


if __name__ == '__main__':
    unittest.main()
