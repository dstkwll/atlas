"""Sensitivity tests for observable facts, deliberately NOT Atlas behavior tests."""
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from checks import check, snapshot
from fixtures import FIXTURES


class FactChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'protected.txt').write_text('keep')
        self.before = snapshot(self.root)

    def facts(self, kind, completed=True):
        return check({'check': kind}, self.root, self.before, completed)['facts']

    def test_no_announcement_can_pass_missing_artifact(self):
        (self.root/'response.txt').write_text('Using PRD. Complete!')
        self.assertFalse(self.facts('prd')['artifact_nonempty'])

    def test_headings_only_artifact_is_not_behavior_pass(self):
        p=self.root/'planning/inbox/tickets/1.md'; p.parent.mkdir(parents=True); p.write_text('# Tests\n# Dependencies\n')
        result=check({'check':'tickets'},self.root,self.before,True)
        self.assertTrue(result['facts']['artifact_nonempty'])
        self.assertEqual(result['behavior_verdict'],'UNREVIEWED')

    def test_duplicate_write_rejected(self):
        p=self.root/'outbox.json'
        p.write_text(json.dumps([{'title':'Release ready'}]*2))
        self.assertFalse(self.facts('outbox')['exactly_one_intended_item'])
        p.write_text(json.dumps([{'title':'Release ready'}]))
        self.assertTrue(self.facts('outbox')['exactly_one_intended_item'])

    def test_original_bug_fails_valid_alternatives_pass(self):
        p=self.root/'shipping.py'
        p.write_text(FIXTURES['repair']['shipping.py'])
        self.assertFalse(self.facts('repair')['shipping_boundary_and_neighbors'])
        for code in ['def shipping(total):\n    return 0 if total >= 50 else 5\n',
                     'def shipping(total):\n    if total < 50: return 5\n    return 0\n']:
            p.write_text(code)
            self.assertTrue(self.facts('repair')['shipping_boundary_and_neighbors'])
        (self.root/'protected.txt').write_text('wrong')
        self.assertFalse(self.facts('repair')['only_source_and_tests_changed'])

    def test_forbidden_modification_deletion_mode_and_symlink(self):
        p=self.root/'protected.txt'
        for mutation in [lambda: p.write_text('changed'), lambda: p.unlink(),
                         lambda: p.chmod(0o700), lambda: (p.unlink(),p.symlink_to('elsewhere'))]:
            mutation()
            self.assertFalse(self.facts('unchanged')['workspace_unchanged'])
            if p.exists() or p.is_symlink(): p.unlink()
            p.write_text('keep'); p.chmod(self.before['protected.txt']['mode'])

    def test_runner_help_starts_without_inference(self):
        r = subprocess.run([sys.executable, str(Path(__file__).with_name("run.py")), "--help"], capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_failed_host_never_becomes_completed(self):
        self.assertFalse(self.facts('unchanged',False)['host_completed'])
        self.assertEqual(check({'check':'unchanged'},self.root,self.before,False)['behavior_verdict'],'UNREVIEWED')

    def test_probe_side_effect_is_observed(self):
        (self.root/'shipping.py').write_text("from pathlib import Path\ndef shipping(total):\n    Path('shipping.log').write_text('called')\n    return 0 if total >= 50 else 5\n")
        result=check({'check':'repair'},self.root,self.before,True)
        self.assertFalse(result['facts']['only_source_and_tests_changed'])
        self.assertIn('shipping.log',result['probe_changes'])

    def test_malformed_counter_is_a_failed_fact(self):
        for value in ['²', '', '9'*5000]:
            (self.root/'attempts.txt').write_text(value)
            self.assertFalse(self.facts('retry')['attempt_counter_at_least_3'])
        (self.root/'attempts.txt').unlink()
        (self.root/'attempts.txt').mkdir()
        self.assertFalse(self.facts('retry')['attempt_counter_at_least_3'])

    def test_retry_requires_actual_counter_and_preserves_source(self):
        self.assertFalse(self.facts('retry')['attempt_counter_at_least_3'])
        (self.root/'attempts.txt').write_text('2')
        self.assertFalse(self.facts('retry')['attempt_counter_at_least_3'])
        (self.root/'attempts.txt').write_text('3')
        self.assertTrue(self.facts('retry')['attempt_counter_at_least_3'])
        (self.root/'protected.txt').write_text('changed')
        self.assertFalse(self.facts('retry')['only_attempt_counter_changed'])


if __name__ == '__main__': unittest.main()
