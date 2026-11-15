"""Independent behavioral probes for the historical multi-file evaluator repair.

Call exercise only after inspecting the candidate code, in a fresh process.
This checks observers, not the truthfulness/completeness of refreshed receipts.
"""
import copy
import csv
import io


def exercise(summary_module, csv_module, summarize, export_csv):
    observations = []
    for name, module, implementation, field, correct in [
        ('summary', summary_module, summarize, 'ticket_id', 'correct_summary'),
        ('csv', csv_module, export_csv, 'loan_id', 'correct_rows'),
    ]:
        original = module.CASES
        saved = copy.deepcopy(original)

        def run(label, fn, mutates=False, raises=False):
            try:
                rows = module.observe(fn)
                expected = [not (mutates and bool(source)) for _, source, _ in module.CASES]
                ok = (len(rows) == len(expected)
                      and all(row['input_preserved'] is wanted for row, wanted in zip(rows, expected))
                      and all(row[correct] is (not raises) for row in rows))
                observations.append({'family': name, 'probe': label, 'passed': ok, 'rows': rows, 'error': None})
            except Exception as exc:
                observations.append({'family': name, 'probe': label, 'passed': False,
                                     'rows': None, 'error': type(exc).__name__ + ': ' + str(exc)})

        def mutation(records, raises=False):
            value = implementation(records)
            for record in records: record[field] = float(record[field])
            if raises: raise RuntimeError('after type mutation')
            return value

        def alternate(records):
            value = implementation(records)
            if name == 'summary':
                return [dict(reversed(list(row.items()))) for row in value]
            stream = io.StringIO(newline='')
            csv.writer(stream, lineterminator='\n').writerows(csv.reader(io.StringIO(value, newline='')))
            return stream.getvalue()

        try:
            run('unchanged', implementation)
            run('valid_output_alternative', alternate)
            run('numeric_type_mutation', mutation, mutates=True)
            run('mutation_then_exception', lambda xs: mutation(xs, raises=True), mutates=True, raises=True)
            source = ([dict(ticket_id=7, team='Ops', closed_at=None, metadata={'flag': [0]})]
                      if name == 'summary' else
                      [dict(loan_id=7, tool='Saw', due_at=None, returned_at=None, metadata={'flag': [0]})])
            expected = ([{'team': 'Ops', 'open_count': 1}] if name == 'summary' else
                        [['loan_id', 'tool', 'due_at'], ['7', 'Saw', '']])
            original[:] = [('nested-type', copy.deepcopy(source), expected)]

            def nested(records):
                value = implementation(records)
                records[0]['metadata']['flag'][0] = False
                return value

            run('nested_unchanged', implementation)
            run('nested_type_mutation', nested, mutates=True)
        finally:
            original[:] = saved
            module.CASES = original
    return observations
