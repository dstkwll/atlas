"""Supplemental probes added after PR71 review; original twelve stay frozen.

Inspect candidate code before calling exercise_values in a separate process.
These check same-type top-level integer-ID mutations, not receipts.
"""


def exercise_values(summary_module, csv_module, summarize, export_csv):
    observations = []
    for name, module, implementation, field, correct in [
        ('summary', summary_module, summarize, 'ticket_id', 'correct_summary'),
        ('csv', csv_module, export_csv, 'loan_id', 'correct_rows'),
    ]:
        for raises in (False, True):
            def mutation(records):
                value = implementation(records)
                for record in records:
                    record[field] += 1
                if raises:
                    raise RuntimeError('after value mutation')
                return value

            label = 'value_mutation_then_exception' if raises else 'value_mutation'
            try:
                rows = module.observe(mutation)
                expected = [not bool(source) for _, source, _ in module.CASES]
                ok = (len(rows) == len(expected)
                      and all(row['input_preserved'] is wanted for row, wanted in zip(rows, expected))
                      and all(row[correct] is (not raises) for row in rows))
                observations.append({'family': name, 'probe': label, 'passed': ok,
                                     'rows': rows, 'error': None})
            except Exception as exc:
                observations.append({'family': name, 'probe': label, 'passed': False,
                                     'rows': None, 'error': type(exc).__name__ + ': ' + str(exc)})
    return observations
