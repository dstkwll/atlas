import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from checks import snapshot, check
from fixtures import FIXTURES
from transfer_artifact import prepare
from transfer_checks import observe


def reference(loans):
    s = io.StringIO(newline=''); w = csv.writer(s, lineterminator='\n')
    w.writerow(['loan_id','tool','due_at'])
    for r in sorted((r for r in loans if r['returned_at'] is None), key=lambda r:(r['tool'],r['loan_id'])):
        w.writerow([r['loan_id'],r['tool'],r['due_at']])
    return s.getvalue()


class TransferTests(unittest.TestCase):
    def test_checker_accepts_valid_line_endings_and_rejects_defects(self):
        def ok(fn): return all(r['correct_rows'] and r['input_preserved'] for r in observe(fn))
        self.assertTrue(ok(reference))
        self.assertTrue(ok(lambda loans: reference(loans).replace('\n','\r\n') if not any('\n' in r['tool'] for r in loans) else reference(loans)))
        self.assertFalse(ok(lambda loans: reference([])))
        self.assertFalse(ok(lambda loans: reference(loans).replace('loan_id,tool,due_at','loan_id,tool,due_at,borrower')))
        def mutation(loans):
            loans.reverse(); return reference(loans)
        self.assertFalse(ok(mutation))
        def swapped(loans):
            s=reference(loans); return s.replace('2,Saw,\n10,Saw,unparsed date','10,Saw,unparsed date\n2,Saw,')
        self.assertFalse(ok(swapped))

    def test_primary_and_case_sensitive_order_mutants_fail(self):
        for key in (lambda r:r['loan_id'], lambda r:(r['tool'].casefold(),r['loan_id'])):
            def mutant(loans):
                s=io.StringIO();w=csv.writer(s);w.writerow(['loan_id','tool','due_at'])
                for r in sorted((r for r in loans if r['returned_at'] is None),key=key):
                    w.writerow([r['loan_id'],r['tool'],r['due_at']])
                return s.getvalue()
            self.assertFalse(all(r['correct_rows'] for r in observe(mutant)))

    def test_edited_deliverable_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ws,out=self.producer(root)
            (out/'prd.md').write_text('post hoc repaired artifact')
            with self.assertRaises(ValueError): prepare(root)

    def producer(self, root):
        ws=root/'workspace'; ws.mkdir()
        for k,v in FIXTURES['transfer-export'].items(): (ws/k).write_text(v)
        (root/'before.json').write_text(json.dumps(snapshot(ws)))
        (root/'metadata.json').write_text(json.dumps({'case':{'id':'transfer-prd'}}))
        (root/'result.json').write_text(json.dumps({'status':'completed','facts':{'only_planning_changed':True}}))
        out=ws/'planning/deliverable';out.mkdir(parents=True)
        (out/'prd.md').write_text('Artifact text with unresolved decisions')
        (ws/'planning/private.md').write_text('Private author notes')
        (root/'after.json').write_text(json.dumps(snapshot(ws)))
        return ws,out

    def test_partial_deliverable_deletion_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ws,out=self.producer(root)
            (out/'acceptance.md').write_text('Additional acceptance criteria')
            (root/'after.json').write_text(json.dumps(snapshot(ws)))
            self.assertIn('planning/deliverable/acceptance.md', prepare(root))
            (out/'acceptance.md').unlink()
            with self.assertRaises(ValueError): prepare(root)

    def test_only_exact_artifact_and_unchanged_code_transfer(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ws,out=self.producer(root)
            got=prepare(root)
            self.assertEqual(set(got), {'loans.py','csv_export.py','planning/deliverable/prd.md'})
            self.assertEqual(got['planning/deliverable/prd.md'], (out/'prd.md').read_text())
            (ws/'loans.py').write_text('changed')
            with self.assertRaises(ValueError): prepare(root)

    def test_missing_symlink_and_extra_file_rejected(self):
        for mode in ['missing','symlink','python']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root=Path(d);ws,out=self.producer(root)
                if mode=='missing': (out/'prd.md').unlink()
                elif mode=='symlink': (out/'linked.md').symlink_to(ws/'BRIEF.md')
                else: (out/'run.py').write_text('raise SystemExit')
                with self.assertRaises(ValueError): prepare(root)

    def test_consumer_boundary_preserves_sources_and_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'loans.py').write_text('source')
            before=snapshot(root); (root/'csv_export.py').write_text('implementation')
            self.assertTrue(check({'check':'transfer-consumer'},root,before,True)['facts']['only_export_tests_planning_changed'])
            (root/'.pytest_cache').mkdir(); (root/'.pytest_cache/x').write_text('cache')
            self.assertTrue(check({'check':'transfer-consumer'},root,before,True)['facts']['only_export_tests_planning_changed'])
            (root/'planning/deliverable').mkdir(parents=True)
            (root/'planning/deliverable/prd.md').write_text('changed artifact')
            self.assertFalse(check({'check':'transfer-consumer'},root,before,True)['facts']['only_export_tests_planning_changed'])
            (root/'loans.py').write_text('changed')
            self.assertFalse(check({'check':'transfer-consumer'},root,before,True)['facts']['only_export_tests_planning_changed'])
