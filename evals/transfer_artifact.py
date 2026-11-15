#!/usr/bin/env python3
"""Stage a fresh consumer from an inspected CSV or dependency-PRD producer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

import run

SOURCE_FILES = ('loans.py', 'csv_export.py')
PRODUCERS = {'transfer-prd', 'transfer-tickets', 'transfer-handoff', 'dependency-prd', 'conflict-prd'}
CONFLICT_FILES = ('evals/dependency_checks.py', 'evals/transfer_checks.py',
                  'examples/queue_summary.py', 'examples/csv_export.py', 'examples/loans.py',
                  'evidence/summary-original.json', 'evidence/csv-original.json', 'smoke.py')
ATTRIBUTION_PATH = 'planning/deliverable/evidence-attribution.md'


def producer_id(root):
    return json.loads(regular_text(root / 'metadata.json'))['case']['id']


def consumer_case(producer):
    if producer not in PRODUCERS:
        raise ValueError('Unknown transfer producer')
    if producer == 'conflict-prd':
        return {'id': 'conflict-consumer', 'fixture': 'conflict-consumer', 'git_root': True,
                'check': 'conflict-consumer', 'turns': [
                    'Read planning/deliverable/ and the supplied project. You are authorized to implement the ready maintenance described by the PRD and record local verification. Respect its unresolved decisions and preserve the received documents. If necessary intent is missing, record the blocker under planning/ instead of inventing it. Use only this project; no external services, installation or publication.']}
    dependency = producer == 'dependency-prd'
    key = 'dependency-consumer' if dependency else 'transfer-consumer'
    scope = ('Implement the work declared ready and run useful local tests. Preserve planning/deliverable/. '
             if dependency else
             'Implement in csv_export.py and run useful local tests. Preserve loans.py and planning/deliverable/. ')
    return {'id': key, 'fixture': key, 'git_root': True, 'check': key, 'turns': [
        'Read the supplied planning/deliverable/ documents and current code. You are authorized to implement the work that the artifact declares ready, respecting its scope and unresolved decisions. '
        + scope + 'If required intent is missing, record the exact blocker under planning/ rather than inventing policy. Use only this project; no external services, installation or publication.']}


def regular_text(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Expected regular file: ' + str(path))
    return path.read_bytes().decode('utf-8')


def prepare(root, *, evidence_attribution=False):
    # Local maintainer input, not a security sandbox. Resolve the selected trial once.
    root = root.resolve()
    result = json.loads(regular_text(root / 'result.json'))
    name = producer_id(root)
    if name not in PRODUCERS or result['status'] != 'completed' or not result['facts'].get('only_planning_changed'):
        raise ValueError('Expected a completed planning-only transfer producer')
    if evidence_attribution and name != 'conflict-prd':
        raise ValueError('Evidence-attribution clarification requires a conflict-prd producer')
    workspace = root / 'workspace'
    if workspace.is_symlink():
        raise ValueError('Workspace must not be a symlink')
    before = json.loads(regular_text(root / 'before.json'))
    after = json.loads(regular_text(root / 'after.json'))
    fixture = {}
    source_files = (CONFLICT_FILES if name == 'conflict-prd' else
                    ('queue_summary.py', 'delivery.py') if name == 'dependency-prd' else SOURCE_FILES)
    for name in source_files:
        content = regular_text(workspace / name)
        if hashlib.sha256(content.encode()).hexdigest() != before[name]['sha256']:
            raise ValueError('Producer source changed: ' + name)
        fixture[name] = content
    planning = workspace / 'planning'
    deliverable = planning / 'deliverable'
    if planning.is_symlink() or deliverable.is_symlink() or not deliverable.is_dir():
        raise ValueError('Missing regular deliverable directory')
    for path in sorted(deliverable.rglob('*')):
        if path.is_symlink():
            raise ValueError('Deliverable contains a symlink')
        if path.is_dir():
            continue
        if path.suffix != '.md':
            raise ValueError('Expected only requested Markdown deliverables')
        key = str(path.relative_to(workspace))
        content = regular_text(path)
        if hashlib.sha256(content.encode()).hexdigest() != after.get(key, {}).get('sha256'):
            raise ValueError('Deliverable changed after producer completion: ' + key)
        fixture[key] = content
    expected = {k for k, v in after.items()
                if k.startswith('planning/deliverable/') and 'sha256' in v}
    actual = {k for k in fixture if k.startswith('planning/deliverable/')}
    if actual != expected:
        raise ValueError('Deliverable inventory changed after producer completion')
    if not any(k.startswith('planning/deliverable/') and v.strip() for k,v in fixture.items()):
        raise ValueError('No nonempty deliverable was produced')
    if evidence_attribution:
        if ATTRIBUTION_PATH in fixture:
            raise ValueError('Evidence-attribution path conflicts with an original deliverable')
        fixture[ATTRIBUTION_PATH] = regular_text(Path(__file__).with_name('attribution-addendum.md'))
    return fixture


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('producer', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--model')
    p.add_argument('--effort', default='low', choices=['low','medium','high'])
    p.add_argument('--timeout', type=int, default=300)
    p.add_argument('--auth-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')))
    p.add_argument('--preview', action='store_true')
    p.add_argument('--evidence-attribution', action='store_true',
                   help='Add the explicit evidence clarification to a conflict-prd transfer')
    args = p.parse_args()
    if not 1 <= args.timeout <= 600:
        p.error('--timeout must be between 1 and 600 seconds')
    fixture = prepare(args.producer, evidence_attribution=args.evidence_attribution)
    manifest = {k: hashlib.sha256(v.encode()).hexdigest() for k,v in fixture.items()}
    if args.preview:
        print(json.dumps(manifest, indent=2)); return
    if not args.output or not args.model:
        p.error('--output and --model required for execution')
    case = consumer_case(producer_id(args.producer))
    key = case['id']
    run.FIXTURES[key] = fixture
    args.condition = 'unguided'
    output = args.output.resolve()
    if output.exists():
        p.error('Output directory must not already exist')
    source_record = {'producer':str(args.producer.resolve()), 'files':manifest,
        'evidence_attribution':args.evidence_attribution,
        'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        completed = run.trial(case, args, output)
    finally:
        if output.is_dir():
            (output/'transfer-source.json').write_text(json.dumps(source_record, indent=2))
    raise SystemExit(0 if completed else 1)


if __name__ == '__main__':
    main()
