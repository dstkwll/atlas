"""Task-derived checks for the bounded loan-export transfer diagnostic."""
import copy
import csv
import io

HEADER = ['loan_id', 'tool', 'due_at']
CASES = [
    ('empty', [], [HEADER]),
    ('returned', [dict(loan_id=1, tool='Drill', due_at=None, returned_at='')], [HEADER]),
    ('ordering_filter_and_blank', [
        dict(loan_id=10, tool='Saw', due_at='unparsed date', returned_at=None, borrower='Private A'),
        dict(loan_id=2, tool='Saw', due_at=None, returned_at=None, borrower='Private B'),
        dict(loan_id=9, tool='Axe', due_at='later', returned_at='done'),
        dict(loan_id=1, tool='Drill', due_at='2026-04-01', returned_at=None)],
        [HEADER, ['1','Drill','2026-04-01'], ['2','Saw',''], ['10','Saw','unparsed date']]),
    ('primary_and_exact_string_order', [
        dict(loan_id=1, tool='anvil', due_at=None, returned_at=None),
        dict(loan_id=20, tool='Axe', due_at=None, returned_at=None),
        dict(loan_id=3, tool='Saw', due_at=None, returned_at=None)],
        [HEADER, ['20','Axe',''], ['3','Saw',''], ['1','anvil','']]),
    ('quoted_fields', [dict(loan_id=7, tool='Clamp, "wide"\nA', due_at='literal,date',
                           returned_at=None, borrower='Private C', extra='not exported')],
        [HEADER, ['7', 'Clamp, "wide"\nA', 'literal,date']]),
]


def observe(export_csv):
    results = []
    for name, source, expected in CASES:
        loans = copy.deepcopy(source)
        try:
            raw = export_csv(loans)
            if not isinstance(raw, str):
                raise TypeError('export_csv did not return a string')
            rows = list(csv.reader(io.StringIO(raw, newline=''), strict=True))
            results.append(dict(case=name, correct_rows=rows == expected,
                                input_preserved=loans == source, rows=rows, error=None))
        except Exception as exc:
            results.append(dict(case=name, correct_rows=False, input_preserved=loans == source,
                                rows=None, error=type(exc).__name__ + ': ' + str(exc)))
    return results
