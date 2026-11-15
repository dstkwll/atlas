import json
from pathlib import Path
import tempfile
import unittest

from checks import check, snapshot
from dependency_checks import observe
from fixtures import FIXTURES
from transfer_artifact import consumer_case, prepare


def reference(tickets):
    counts = {}
    for ticket in tickets:
        if ticket['closed_at'] is None:
            team = ticket['team']
            counts[team] = counts.get(team, 0) + 1
    return [{'team': team, 'open_count': counts[team]} for team in sorted(counts)]


def passes(fn):
    return all(row['correct_summary'] and row['input_preserved'] for row in observe(fn))


class DependencyTests(unittest.TestCase):
    def test_valid_implementations_and_key_order(self):
        self.assertTrue(passes(reference))
        self.assertTrue(passes(lambda xs: [dict(reversed(list(row.items()))) for row in reference(xs)]))

    def test_wrong_filter_order_normalization_and_leakage_fail(self):
        def all_rows(xs):
            return reference([dict(x, closed_at=None) for x in xs])
        def normalized(xs):
            return reference([dict(x, team=x['team'].strip().lower()) for x in xs])
        for fn in [lambda xs: [], all_rows, normalized,
                   lambda xs: list(reversed(reference(xs))),
                   lambda xs: [dict(row, title='private') for row in reference(xs)],
                   lambda xs: [dict(row, open_count=True) for row in reference(xs)]]:
            with self.subTest(fn=fn): self.assertFalse(passes(fn))

    def test_blocked_ready_work_and_mutation_fail(self):
        def blocked(xs):
            raise NotImplementedError('Waiting for delivery contract')
        def mutation(xs):
            result = reference(xs)
            for row in xs:
                if 'metadata' in row: row['metadata']['labels'].append('changed')
            xs.reverse()
            return result
        self.assertFalse(passes(blocked))
        self.assertFalse(passes(mutation))

    def test_casefold_and_busiest_sort_fail(self):
        for key in [lambda row: row['team'].casefold(),
                    lambda row: (-row['open_count'], row['team'])]:
            self.assertFalse(passes(lambda xs: sorted(reference(xs), key=key)))

    def test_dependency_packet_omits_author_context_in_both_conditions(self):
        for condition in ['guided', 'unguided']:
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as d:
                root=Path(d);ws=root/'workspace';ws.mkdir()
                for name,content in FIXTURES['dependency-prd'].items(): (ws/name).write_text(content)
                (root/'metadata.json').write_text(json.dumps({'case':{'id':'dependency-prd'},'condition':condition}))
                (root/'result.json').write_text(json.dumps({'status':'completed','facts':{'only_planning_changed':True}}))
                (root/'before.json').write_text(json.dumps(snapshot(ws)))
                artifact=ws/'planning/deliverable';artifact.mkdir(parents=True)
                (artifact/'prd.md').write_text('Actual authored requirements')
                (root/'after.json').write_text(json.dumps(snapshot(ws)))
                packet=prepare(root)
                self.assertEqual(set(packet), {'queue_summary.py','delivery.py','planning/deliverable/prd.md'})
                self.assertEqual(packet['planning/deliverable/prd.md'], 'Actual authored requirements')
                (ws/'delivery.py').write_text('Unauthorized implementation')
                with self.assertRaises(ValueError): prepare(root)

    def test_consumer_boundary_rejects_delivery_and_artifact_changes(self):
        for target in ['delivery.py','planning/deliverable/prd.md']:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as d:
                root=Path(d);(root/'planning/deliverable').mkdir(parents=True)
                (root/'delivery.py').write_text('original')
                (root/'planning/deliverable/prd.md').write_text('original')
                before=snapshot(root);(root/'queue_summary.py').write_text('ready implementation')
                case=consumer_case('dependency-prd')
                self.assertEqual(case['check'],'dependency-consumer')
                self.assertTrue(check(case,root,before,True)['facts']['only_summary_tests_planning_changed'])
                (root/target).write_text('changed')
                self.assertFalse(check(case,root,before,True)['facts']['only_summary_tests_planning_changed'])
        self.assertEqual(consumer_case('transfer-prd')['check'], 'transfer-consumer')
        with self.assertRaises(ValueError): consumer_case('unknown')
