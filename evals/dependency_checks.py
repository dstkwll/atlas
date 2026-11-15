"""Task-derived examples for the ready portion of the dependency PRD diagnostic."""
import copy


CASES = [
    ('empty', [], []),
    ('all_closed', [
        dict(ticket_id=1, team='Ops', closed_at=''),
        dict(ticket_id=2, team='Ops', closed_at=False)], []),
    ('exact_codepoint_order', [
        dict(ticket_id=1, team='alpha', closed_at=None),
        dict(ticket_id=2, team='Zeta', closed_at=None),
        dict(ticket_id=3, team='Zeta', closed_at=None),
        dict(ticket_id=4, team='Beta', closed_at=None)],
        [{'team': 'Beta', 'open_count': 1}, {'team': 'Zeta', 'open_count': 2},
         {'team': 'alpha', 'open_count': 1}]),
    ('group_filter_and_order', [
        dict(ticket_id=10, team='Support', closed_at=None),
        dict(ticket_id=2, team='Ops', closed_at=None),
        dict(ticket_id=7, team='Ops', closed_at=None),
        dict(ticket_id=3, team='support', closed_at=None),
        dict(ticket_id=1, team='Accounts', closed_at='done'),
        dict(ticket_id=4, team='Ops', closed_at=0)],
        [{'team': 'Ops', 'open_count': 2}, {'team': 'Support', 'open_count': 1},
         {'team': 'support', 'open_count': 1}]),
    ('exact_names_and_private_extras', [
        dict(ticket_id=1, team=' Ops', closed_at=None, customer_email='private@example.invalid',
             title='Sensitive issue', metadata={'labels': ['private']}),
        dict(ticket_id=2, team='Ops ', closed_at=None),
        dict(ticket_id=3, team='Ops', closed_at=None)],
        [{'team': ' Ops', 'open_count': 1}, {'team': 'Ops', 'open_count': 1},
         {'team': 'Ops ', 'open_count': 1}]),
]


def observe(summarize):
    results = []
    for name, source, expected in CASES:
        tickets = copy.deepcopy(source)
        try:
            value = summarize(tickets)
            shape = (isinstance(value, list) and all(
                isinstance(row, dict) and type(row.get('open_count')) is int for row in value))
            results.append(dict(case=name, correct_summary=shape and value == expected,
                                input_preserved=tickets == source, observed=value, error=None))
        except Exception as exc:
            results.append(dict(case=name, correct_summary=False, input_preserved=tickets == source,
                                observed=None, error=type(exc).__name__ + ': ' + str(exc)))
    return results
