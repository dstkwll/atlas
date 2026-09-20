"""Check packet controls and real fixture behavior, not agent correctness."""
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from delegation import CONTRACT, SCENARIOS, fixture, observe, prepare


def exercise(scenario, mode):
    files = fixture(scenario)
    provider_module, candidate_module = {}, {}
    exec(compile(files['provider.py'], 'provider.py', 'exec'), provider_module)
    exec(compile(files['candidate.py'], 'candidate.py', 'exec'), candidate_module)
    provider = provider_module['Provider'](mode)
    result = candidate_module['deliver'](provider, 'payload')
    return provider, result


class DelegationPackets(unittest.TestCase):
    def test_lost_ack_and_rejection_discriminate_regression_from_control(self):
        bad, bad_result = exercise('regression', 'lost_ack')
        good, good_result = exercise('control', 'lost_ack')
        self.assertEqual(len(bad.effects), 2)
        self.assertEqual(len(good.effects), 1)
        self.assertEqual(bad.calls, 2)
        self.assertEqual(good.calls, 2)
        self.assertEqual(good_result['status'], 'complete')
        self.assertEqual(bad_result['status'], 'complete')
        bad, result = exercise('regression', 'reject')
        self.assertEqual(result['status'], 'complete')
        good, result = exercise('control', 'reject')
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(good.effects, [])
        for scenario, expected in (('regression', True), ('control', False)):
            candidate = ModuleType('candidate')
            exec(compile(fixture(scenario)['candidate.py'], 'candidate.py', 'exec'), candidate.__dict__)
            caller = {}
            with patch.dict(sys.modules, {'candidate': candidate}):
                exec(compile(fixture(scenario)['caller.py'], 'caller.py', 'exec'), caller)
                provider_types = {}
                exec(fixture(scenario)['provider.py'], provider_types)
                self.assertEqual(caller['run'](provider_types['Provider']('reject'), 'payload'), expected)

    def test_exhaustion_is_bounded_and_uncertainty_is_not_a_fake_runtime_defect(self):
        for scenario in SCENARIOS:
            provider, result = exercise(scenario, 'unavailable')
            self.assertEqual(provider.calls, 2)
            self.assertEqual(result['status'], 'unknown')
            provider, result = exercise(scenario, 'normal')
            self.assertEqual(provider.calls, 1)
            self.assertEqual(result['status'], 'complete')
        provider, result = exercise('uncertain', 'lost_ack')
        self.assertEqual(len(provider.effects), 1)
        self.assertEqual(result['status'], 'complete')

    def test_matched_packets_hide_grading_material_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'batch'
            manifest = prepare(output)
            self.assertEqual(len(manifest['schedule']), 9)
            self.assertEqual(len({(r['scenario'], r['condition']) for r in manifest['schedule']}), 9)
            for row in manifest['schedule']:
                root = output / row['trial'] / 'workspace'
                self.assertEqual((root/'roles/failure-reviewer.md').read_text(), CONTRACT)
                self.assertIn(CONTRACT, (root/'task.md').read_text())
                for name, content in fixture(row['scenario']).items():
                    self.assertEqual((root/name).read_text(), content)
                self.assertFalse((root/'schedule.json').exists())
                self.assertFalse((root/'delegation-review.md').exists())
                self.assertFalse((root/'test_delegation.py').exists())
            with self.assertRaises(FileExistsError):
                prepare(output)

    def test_observations_do_not_pass_behavior_or_trust_claimed_workers(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'batch'
            prepare(output)
            trial = output / 'trial-01'
            self.assertFalse(observe(trial)['facts']['review_nonempty_regular_file'])
            root = trial/'workspace'
            (root/'results/review.md').write_text('All good. A worker reviewed everything.')
            result = observe(trial)
            self.assertTrue(result['facts']['only_results_changed_in_observed_paths'])
            self.assertTrue(result['facts']['review_nonempty_regular_file'])
            self.assertEqual(result['behavior_verdict'], 'UNREVIEWED')
            self.assertEqual(result['worker_execution'], 'UNVERIFIED')
            for path, mutation in (
                ('candidate.py', lambda p: p.write_text('changed')),
                ('provider.py', lambda p: p.unlink()),
                ('caller.py', lambda p: p.chmod(0o700)),
            ):
                mutation(root/path)
                self.assertFalse(observe(trial)['facts']['only_results_changed_in_observed_paths'])
            (root/'results/review.md').unlink()
            (root/'results/review.md').symlink_to('../requirements.md')
            self.assertFalse(observe(trial)['facts']['review_nonempty_regular_file'])


if __name__ == '__main__':
    unittest.main()
