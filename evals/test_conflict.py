import json
import hashlib
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import dependency_checks
import transfer_checks
from checks import check, snapshot
from conflict_checks import exercise
from conflict_value_checks import exercise_values
from fixtures import FIXTURES
from transfer_artifact import CONFLICT_FILES, consumer_case, prepare


def historical(name):
    module = types.ModuleType(name)
    exec(FIXTURES['conflict-prd']['evals/' + name + '.py'], module.__dict__)
    return module


def examples():
    modules={name:types.ModuleType(name) for name in ['queue_summary','loans','csv_export']}
    with patch.dict('sys.modules', modules):
        for name in ['queue_summary','loans','csv_export']:
            exec(FIXTURES['conflict-prd']['examples/'+name+'.py'],modules[name].__dict__)
    return modules['queue_summary'].summarize,modules['csv_export'].export_csv


summary,csv_export=examples()


class ConflictTests(unittest.TestCase):
    def test_value_probes_retain_original_and_repaired_detection(self):
        for modules in [(historical('dependency_checks'), historical('transfer_checks')),
                        (dependency_checks, transfer_checks)]:
            rows = exercise_values(*modules, summary, csv_export)
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(row['passed'] for row in rows))

    def test_type_only_comparator_passes_original_but_fails_value_probes(self):
        def types_only(left, right):
            if type(left) is not type(right):
                return False
            if isinstance(left, dict):
                return left.keys() == right.keys() and all(
                    types_only(left[key], right[key]) for key in left)
            if isinstance(left, (list, tuple)):
                return len(left) == len(right) and all(
                    types_only(a, b) for a, b in zip(left, right))
            return True  # Deliberately ignores scalar values.

        modules = []
        for name, data in [('dependency_checks', 'tickets'), ('transfer_checks', 'loans')]:
            text = FIXTURES['conflict-prd']['evals/' + name + '.py']
            text = text.replace(data + ' == source', 'types_only(' + data + ', source)')
            module = types.ModuleType(name)
            module.types_only = types_only
            exec(text, module.__dict__)
            modules.append(module)
        original = exercise(*modules, summary, csv_export)
        self.assertEqual(len(original), 12)
        self.assertTrue(all(row['passed'] for row in original))
        supplemental = exercise_values(*modules, summary, csv_export)
        self.assertEqual(len(supplemental), 4)
        self.assertTrue(all(not row['passed'] for row in supplemental))
        for row in supplemental:
            self.assertIsNone(row['error'])
            self.assertTrue(all(result['input_preserved'] is True for result in row['rows']))
            correct = 'correct_summary' if row['family'] == 'summary' else 'correct_rows'
            expected = row['probe'] == 'value_mutation'
            self.assertTrue(all(result[correct] is expected for result in row['rows']))

    def test_original_defect_and_complete_repair(self):
        old_summary, old_csv = historical('dependency_checks'), historical('transfer_checks')
        original = exercise(old_summary, old_csv, summary, csv_export)
        for family in ['summary', 'csv']:
            rows = {r['probe']: r['passed'] for r in original if r['family']==family}
            self.assertTrue(rows['unchanged']); self.assertTrue(rows['valid_output_alternative'])
            self.assertFalse(rows['numeric_type_mutation'])
            self.assertFalse(rows['mutation_then_exception'])
            self.assertFalse(rows['nested_type_mutation'])
        self.assertTrue(all(r['passed'] for r in exercise(dependency_checks, transfer_checks, summary, csv_export)))

    def test_summary_only_repair_does_not_hide_csv_failure(self):
        rows=exercise(dependency_checks,historical('transfer_checks'),summary,csv_export)
        self.assertTrue(all(r['passed'] for r in rows if r['family']=='summary'))
        self.assertTrue(any(not r['passed'] for r in rows if r['family']=='csv'))

    def test_bound_case_list_alternative_and_bad_preservation_controls(self):
        modules=[]
        for name, arg, data in [('dependency_checks','summarize','tickets'),('transfer_checks','export_csv','loans')]:
            text=FIXTURES['conflict-prd']['evals/'+name+'.py']
            fixed=text.replace(data+' == source', 'json.dumps('+data+', sort_keys=True) == json.dumps(source, sort_keys=True)')
            fixed=fixed.replace('def observe('+arg+'):', 'def observe('+arg+', cases=CASES):').replace('in CASES:', 'in cases:')
            module=types.ModuleType(name);module.json=json;exec(fixed,module.__dict__);modules.append(module)
        self.assertTrue(all(r['passed'] for r in exercise(*modules,summary,csv_export)))
        for replacement,count in [('False',2),('json.dumps(tickets) == json.dumps(source)',1)]:
            text=FIXTURES['conflict-prd']['evals/dependency_checks.py'].replace('tickets == source',replacement,count)
            module=types.ModuleType('bad');module.json=json;exec(text,module.__dict__)
            self.assertTrue(any(not r['passed'] for r in exercise(module,transfer_checks,summary,csv_export)))

    def test_packet_hashes_and_original_receipt_bindings(self):
        packet=FIXTURES['conflict-prd'];origins=json.loads(packet['origins.json'])
        for path,info in origins['files'].items():
            self.assertEqual(hashlib.sha256(packet[path].encode()).hexdigest(),info['sha256'])
        for receipt,checker,impl in [('summary-original.json','dependency_checks.py','queue_summary.py'),
                                     ('csv-original.json','transfer_checks.py','csv_export.py')]:
            r=json.loads(packet['evidence/'+receipt])
            self.assertEqual(r['checker_sha256'],hashlib.sha256(packet['evals/'+checker].encode()).hexdigest())
            self.assertEqual(r.get('implementation_sha256',r.get('code_sha256')),hashlib.sha256(packet['examples/'+impl].encode()).hexdigest())

    def test_real_transfer_and_evidence_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ws=root/'workspace';ws.mkdir()
            for name,value in FIXTURES['conflict-prd'].items():
                p=ws/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
            before=snapshot(ws)
            (root/'before.json').write_text(json.dumps(before))
            (root/'metadata.json').write_text(json.dumps({'case':{'id':'conflict-prd'}}))
            (root/'result.json').write_text(json.dumps({'status':'completed','facts':{'only_planning_changed':True}}))
            deliverable=ws/'planning/deliverable';deliverable.mkdir(parents=True)
            (deliverable/'prd.md').write_text('Exact actual PRD')
            (root/'after.json').write_text(json.dumps(snapshot(ws)))
            self.assertEqual(set(prepare(root)),set(CONFLICT_FILES)|{'planning/deliverable/prd.md'})
            case=consumer_case('conflict-prd');base=snapshot(ws)
            (ws/'evals/new_comparison.py').write_text('helper')
            fact='original_evidence_examples_and_documents_preserved'
            (ws/'evidence/new.json').write_text('new receipt')
            (ws/'smoke.py').write_text('updated replay adapter')
            self.assertTrue(check(case,ws,base,True)['facts'][fact])
            (ws/'evidence/summary-original.json').write_text('rewritten')
            self.assertFalse(check(case,ws,base,True)['facts'][fact])
            with self.assertRaises(ValueError):prepare(root)
