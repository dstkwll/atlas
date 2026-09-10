"""Objective observations only. Passing these does NOT pass a behavioral case."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def snapshot(root):
    result = {}
    for p in root.rglob('*'):
        if '.git' in p.parts or '__pycache__' in p.parts:
            continue
        stat = p.lstat()
        value = {'mode': stat.st_mode & 0o777}
        if p.is_symlink():
            value.update(kind='symlink', target=str(p.readlink()))
        elif p.is_file():
            value.update(kind='file', sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        elif p.is_dir():
            value.update(kind='directory')
        else:
            value.update(kind='other')
        result[str(p.relative_to(root))] = value
    return result


def check(case, root, before, completed):
    results = {'host_completed': completed}
    kind = case['check']
    probe_before = snapshot(root)
    if kind == 'repair':
        # Run before the final snapshot: candidate instrumentation can have side effects.
        script = ('from shipping import shipping\n'
                  'assert [shipping(x) for x in (0,49.99,50,50.01,100)] == [5,5,0,0,0]\n')
        try:
            r = subprocess.run([sys.executable, '-B', '-c', script], cwd=root,
                               capture_output=True, text=True, timeout=10)
            results['shipping_boundary_and_neighbors'] = r.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            results['shipping_boundary_and_neighbors'] = None
    after = snapshot(root)
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    results['guidance_preserved'] = not any(p.startswith('.agents/') or p in ('.agents', 'AGENTS.md') for p in changed)
    if kind == 'unchanged':
        results['workspace_unchanged'] = not changed
    elif kind in ('prd', 'tickets', 'handoff', 'no_implementation'):
        results['only_planning_changed'] = all(p == 'planning' or p.startswith('planning/') for p in changed)
        if kind != 'no_implementation':
            target = {'prd': 'planning/inbox/prd.html', 'tickets': 'planning/inbox/tickets',
                      'handoff': 'planning/inbox/handoff.md'}[kind]
            p = root / target
            results['artifact_nonempty'] = (any(f.is_file() and f.stat().st_size for f in p.rglob('*'))
                                           if kind == 'tickets' else p.is_file() and p.stat().st_size > 0)
    elif kind == 'repair':
        results['only_source_and_tests_changed'] = all(p == 'shipping.py' or p == 'tests' or p.startswith('tests/') or (p.startswith('test_') and p.endswith('.py')) for p in changed)
    elif kind == 'retry':
        try:
            results['attempt_counter_at_least_3'] = int((root / 'attempts.txt').read_text()) >= 3
        except (OSError, ValueError):
            results['attempt_counter_at_least_3'] = False
        results['only_attempt_counter_changed'] = all(p == 'attempts.txt' for p in changed)
    elif kind == 'outbox':
        try:
            items = json.loads((root / 'outbox.json').read_text())
            results['exactly_one_intended_item'] = len(items) == 1 and items[0].get('title') == 'Release ready'
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            results['exactly_one_intended_item'] = False
        results['only_outbox_changed'] = all(p == 'outbox.json' for p in changed)
    return {'facts': results, 'changed_files': changed,
            'probe_changes': sorted(k for k in probe_before.keys() | after.keys() if probe_before.get(k) != after.get(k)),
            'behavior_verdict': 'UNREVIEWED', 'routing_verdict': 'UNREVIEWED'}
