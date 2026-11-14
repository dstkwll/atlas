"""Control delivery and review integrity, not model-judgment correctness."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import calibrate


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.suite, _ = calibrate.load_controls(calibrate.DEFAULT_CONTROLS)
        self.review = {'judgments': [
            {'control_id': c['id'], 'verdict': c['expected']['verdict'],
             'evidence_refs': [e['id'] for e in c['evidence']], 'reason': 'Synthetic test judgment'}
            for c in self.suite['controls']]}

    def test_packet_withholds_reference_answers_and_private_fields(self):
        suite = copy.deepcopy(self.suite)
        suite['private_note'] = 'secret-suite-marker'
        for c in suite['controls']:
            c['expected']['reason'] = 'secret-answer-marker'
            c['private_note'] = 'secret-case-marker'
            c['evidence'][0]['private_note'] = 'secret-evidence-marker'
        visible = json.dumps(calibrate.packet(suite))
        self.assertNotIn('secret-', visible)
        self.assertTrue(all('expected' not in c for c in calibrate.packet(suite)['controls']))
        self.assertIn(self.suite['controls'][0]['evidence'][0]['text'],
                      calibrate.packet(suite)['controls'][0]['evidence'][0]['text'])

    def test_missing_capture_and_observed_failure_remain_distinct(self):
        self.assertTrue(calibrate.assess(self.suite, self.review)['all_controls_agree'])
        self.review['judgments'][0]['verdict'] = 'UNKNOWN'
        result = calibrate.assess(self.suite, self.review)
        self.assertTrue(result['valid_submission'])
        self.assertFalse(result['all_controls_agree'])
        self.assertFalse(result['controls'][0]['agrees'])
        self.assertTrue(result['controls'][1]['agrees'])

    def test_native_fixture_supplies_only_reviewer_packet(self):
        from fixtures import FIXTURES
        fixture = FIXTURES['calibration-review']
        self.assertEqual(json.loads(fixture['controls.json']), calibrate.packet(self.suite))
        self.assertEqual(set(fixture), {'controls.json', 'BRIEF.md'})
        for control in self.suite['controls']:
            self.assertNotIn(control['expected']['reason'], '\n'.join(fixture.values()))

    def test_missing_duplicate_and_unknown_rows_never_disappear(self):
        for change in ('missing', 'duplicate', 'unknown'):
            review = copy.deepcopy(self.review)
            if change == 'missing': review['judgments'].pop()
            elif change == 'duplicate': review['judgments'].append(review['judgments'][0])
            else: review['judgments'].append({'control_id': 'not-in-suite'})
            with self.subTest(change=change):
                result = calibrate.assess(self.suite, review)
                self.assertFalse(result['valid_submission'])
                self.assertFalse(result['all_controls_agree'])
                self.assertEqual(len(result['controls']), len(self.suite['controls']))

    def test_unsupported_refs_labels_and_missing_reason_are_invalid(self):
        for field, value in [('evidence_refs', ['invented']), ('evidence_refs', []),
                             ('verdict', 'probably pass'), ('verdict', []), ('reason', '')]:
            review = copy.deepcopy(self.review)
            review['judgments'][0][field] = value
            with self.subTest(field=field, value=value):
                result = calibrate.assess(self.suite, review)
                self.assertIsNone(result['controls'][0]['agrees'])
                self.assertFalse(result['all_controls_agree'])

    def test_reference_existence_does_not_claim_entailment(self):
        self.review['judgments'][0].update(reason='Unrelated explanation', evidence_refs=['source'])
        result = calibrate.assess(self.suite, self.review)
        self.assertTrue(result['all_controls_agree'])
        self.assertTrue(result['semantic_review'].startswith('REQUIRED'))

    def test_conflicting_and_unmatched_rows_remain_inspectable(self):
        original = self.review['judgments'][0]
        conflicting = dict(original, verdict='UNKNOWN')
        self.review['judgments'] += [conflicting, {'control_id': 'absent', 'verdict': 'PASS'}, None]
        result = calibrate.assess(self.suite, self.review)
        self.assertEqual(result['controls'][0]['submitted_rows'], [original, conflicting])
        self.assertEqual(len(result['controls'][0]['submission_errors']), 1)
        self.assertEqual(result['unmatched_rows'][0]['row']['verdict'], 'PASS')
        self.assertEqual(result['unmatched_rows'][1]['index'], 10)
        self.assertIsNone(result['unmatched_rows'][1]['row'])
        self.assertFalse(result['all_controls_agree'])

    def test_identity_guard_rejects_changed_inputs_or_references(self):
        with tempfile.TemporaryDirectory() as d:
            controls = Path(d) / 'controls.json'
            review = Path(d) / 'review.json'
            controls.write_text(json.dumps(self.suite))
            review.write_text(json.dumps(self.review))
            _, frozen = calibrate.load_controls(controls)
            visible = calibrate.packet_digest(self.suite)
            cmd = [sys.executable, str(Path(calibrate.__file__)), '--controls', str(controls),
                   '--review', str(review)]
            self.assertEqual(subprocess.run(cmd + ['--expect-controls-sha256', frozen,
                                                   '--expect-packet-sha256', visible], capture_output=True).returncode, 0)
            self.suite['controls'][0]['evidence'][0]['text'] = 'Changed evidence'
            controls.write_text(json.dumps(self.suite))
            self.assertEqual(subprocess.run(cmd + ['--expect-packet-sha256', visible], capture_output=True).returncode, 2)
            self.suite, _ = calibrate.load_controls(calibrate.DEFAULT_CONTROLS)
            self.suite['controls'][0]['expected']['reason'] = 'Changed reference only'
            controls.write_text(json.dumps(self.suite))
            self.assertEqual(subprocess.run(cmd + ['--expect-controls-sha256', frozen], capture_output=True).returncode, 2)

    def test_cli_rejects_duplicate_json_members(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'review.json'
            good = json.dumps(self.review)
            first_verdict = json.dumps(self.review['judgments'][0]['verdict'])
            conflicting_field = good.replace('"verdict": ' + first_verdict,
                                             '"verdict": "UNKNOWN", "verdict": ' + first_verdict, 1)
            conflicting_lists = '{"judgments": [], ' + good[1:]
            for raw in (conflicting_field, conflicting_lists):
                with self.subTest(raw=raw[:60]):
                    path.write_text(raw)
                    result = subprocess.run([sys.executable, str(Path(calibrate.__file__)),
                                             '--review', str(path)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('Duplicate JSON member', result.stderr)
                    self.assertEqual(result.stdout, '')
            controls = Path(d) / 'controls.json'
            controls.write_text(json.dumps(self.suite).replace('"id": ', '"id": "discarded", "id": ', 1))
            result = subprocess.run([sys.executable, str(Path(calibrate.__file__)),
                                     '--controls', str(controls), '--packet'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Duplicate JSON member', result.stderr)

    def test_cli_retains_review_identity_and_distinguishes_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'review.json'
            path.write_text(json.dumps(self.review))
            cmd = [sys.executable, str(Path(calibrate.__file__)), '--review', str(path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertEqual(len(data['review_sha256']), 64)
            self.review['judgments'].pop()
            path.write_text(json.dumps(self.review))
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)
            path.write_text('{}')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            path.write_text('{')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
