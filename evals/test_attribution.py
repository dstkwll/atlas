import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from checks import snapshot
from fixtures import FIXTURES
from transfer_artifact import ATTRIBUTION_PATH, main, prepare


def producer(root, case='conflict-prd', deliverable='prd.md'):
    ws = root / 'workspace'
    ws.mkdir()
    fixture = 'conflict-prd' if case == 'conflict-prd' else 'transfer-export'
    for name, text in FIXTURES[fixture].items():
        p = ws / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (root / 'before.json').write_text(json.dumps(snapshot(ws)))
    (root / 'metadata.json').write_text(json.dumps({'case': {'id': case}}))
    (root / 'result.json').write_text(json.dumps({
        'status': 'completed', 'facts': {'only_planning_changed': True}}))
    out = ws / 'planning/deliverable'
    out.mkdir(parents=True)
    (out / deliverable).write_text('Original artifact; never edit during transfer.')
    (root / 'after.json').write_text(json.dumps(snapshot(ws)))
    return ws


class AttributionTests(unittest.TestCase):
    def test_failed_trial_retains_arm_manifest_and_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'producer'
            root.mkdir()
            producer(root)
            output = Path(directory) / 'trial'
            argv = ['transfer_artifact.py', str(root), '--output', str(output),
                    '--model', 'test-model', '--evidence-attribution']
            def fail(case, args, destination):
                destination.mkdir()
                raise RuntimeError('setup failed')
            with patch('sys.argv', argv), patch('transfer_artifact.run.trial', side_effect=fail):
                with self.assertRaises(RuntimeError):
                    main()
            manifest = (output / 'transfer-source.json').read_bytes()
            data = json.loads(manifest)
            self.assertTrue(data['evidence_attribution'])
            self.assertIn(ATTRIBUTION_PATH, data['files'])
            with patch('sys.argv', argv), patch('transfer_artifact.run.trial') as trial:
                with self.assertRaises(SystemExit):
                    main()
                trial.assert_not_called()
            self.assertEqual((output / 'transfer-source.json').read_bytes(), manifest)

    def test_clarification_is_additive_and_source_trial_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ws = producer(root)
            before = snapshot(ws)
            original = prepare(root)
            clarified = prepare(root, evidence_attribution=True)
            self.assertEqual(set(clarified) - set(original), {ATTRIBUTION_PATH})
            self.assertEqual({k: clarified[k] for k in original}, original)
            self.assertEqual(clarified[ATTRIBUTION_PATH],
                             Path(__file__).with_name('attribution-addendum.md').read_text())
            self.assertEqual(snapshot(ws), before)
            (ws / 'planning/deliverable/prd.md').write_text('Changed original')
            with self.assertRaises(ValueError):
                prepare(root, evidence_attribution=True)

    def test_clarification_cannot_overwrite_an_actual_deliverable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            producer(root, deliverable=Path(ATTRIBUTION_PATH).name)
            self.assertIn(ATTRIBUTION_PATH, prepare(root))
            with self.assertRaises(ValueError):
                prepare(root, evidence_attribution=True)

    def test_clarification_rejects_other_task_families(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            producer(root, case='transfer-prd')
            self.assertTrue(prepare(root))
            with self.assertRaises(ValueError):
                prepare(root, evidence_attribution=True)
