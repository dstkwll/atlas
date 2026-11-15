import unittest

from dependency_checks import observe as summary_observe
from transfer_checks import observe as csv_observe
from test_dependency import reference as summary_reference
from test_transfer import reference as csv_reference
from value_checks import same_value


class ValueTests(unittest.TestCase):
    def test_nested_types_and_mapping_order(self):
        self.assertTrue(same_value({'a': [1, False], 'b': None}, {'b': None, 'a': [1, False]}))
        for a, b in [(1, True), (1, 1.0), ([1], (1,)), ({1: 'x'}, {True: 'x'}),
                     ({'nested': [0]}, {'nested': [False]})]:
            with self.subTest(a=a, b=b): self.assertFalse(same_value(a, b))

    def test_type_mutation_rejected_on_success_and_exception(self):
        for observe, reference, key in [(summary_observe, summary_reference, 'ticket_id'),
                                        (csv_observe, csv_reference, 'loan_id')]:
            for raises in [False, True]:
                def mutant(records):
                    result = reference(records)
                    for record in records: record[key] = float(record[key])
                    if raises: raise RuntimeError('after mutation')
                    return result
                with self.subTest(key=key, raises=raises):
                    rows=observe(mutant)
                    self.assertTrue(any(not row['input_preserved'] for row in rows))
                    self.assertTrue(all(row['input_preserved'] for row in observe(reference)))
