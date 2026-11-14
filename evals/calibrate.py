#!/usr/bin/env python3
"""Prepare blinded controls or audit submitted judgments; never calls a model."""
import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_CONTROLS = Path(__file__).with_name('calibration-controls.json')
VERDICTS = {'PASS', 'FAIL', 'UNKNOWN', 'NOT_APPLICABLE'}


def load_controls(path):
    raw = path.read_bytes()
    suite = json.loads(raw)
    seen = set()
    if not isinstance(suite.get('id'), str) or not suite['id'].strip():
        raise ValueError('A control-set ID is required')
    if not isinstance(suite.get('controls'), list) or not suite['controls']:
        raise ValueError('A nonempty control set is required')
    for control in suite['controls']:
        key = control['id']
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError('Control IDs must be nonempty and unique')
        seen.add(key)
        refs = [e['id'] for e in control['evidence']]
        if not refs or any(not isinstance(r, str) or not r for r in refs) or len(refs) != len(set(refs)):
            raise ValueError('Evidence IDs must be nonempty and unique within a control')
        if any(not isinstance(e.get('text'), str) or not e['text'].strip() for e in control['evidence']):
            raise ValueError('Nonempty evidence text is required')
        if control['expected']['verdict'] not in VERDICTS:
            raise ValueError('Unknown expected verdict')
        if not control['criterion'].strip() or not control['expected']['reason'].strip():
            raise ValueError('Criterion and expected reasoning are required')
    return suite, hashlib.sha256(raw).hexdigest()


def packet(suite):
    # Explicit allowlist: reference verdicts, reasons and future private fields stay out.
    return {'control_set': suite['id'], 'controls': [
        {'id': c['id'], 'criterion': c['criterion'],
         'evidence': [{'id': e['id'], 'text': e['text']} for e in c['evidence']]}
        for c in suite['controls']]}


def packet_digest(suite):
    raw = json.dumps(packet(suite), sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def assess(suite, review):
    """Check coverage, evidence references and reference agreement, not entailment."""
    if not isinstance(review, dict) or not isinstance(review.get('judgments'), list):
        raise ValueError('Review must contain a judgments list')
    known = {c['id']: c for c in suite['controls']}
    submitted = {}
    errors = []
    unmatched = []
    for index, row in enumerate(review['judgments']):
        if not isinstance(row, dict) or not isinstance(row.get('control_id'), str):
            errors.append('Every judgment needs a string control_id')
            unmatched.append({'index': index, 'row': row, 'error': errors[-1]})
            continue
        key = row['control_id']
        if key not in known:
            errors.append('Unknown control: ' + key)
            unmatched.append({'index': index, 'row': row, 'error': errors[-1]})
            continue
        submitted.setdefault(key, []).append(row)
    results = []
    for key, control in known.items():
        rows = submitted.get(key, [])
        issues = []
        if len(rows) != 1:
            issues.append('Expected exactly one judgment; received ' + str(len(rows)))
        row = rows[0] if len(rows) == 1 else {}
        verdict = row.get('verdict')
        if len(rows) == 1 and (not isinstance(verdict, str) or verdict not in VERDICTS):
            issues.append('Invalid or missing verdict')
        reason = row.get('reason')
        if len(rows) == 1 and (not isinstance(reason, str) or not reason.strip()):
            issues.append('Missing reasoning')
        refs = row.get('evidence_refs')
        known_refs = {e['id'] for e in control['evidence']}
        if len(rows) != 1:
            pass
        elif not isinstance(refs, list) or not refs or any(not isinstance(r, str) for r in refs):
            issues.append('A nonempty list of evidence IDs is required')
        elif any(r not in known_refs for r in refs):
            issues.append('Evidence reference does not exist in this control')
        results.append({'control_id': key, 'observed': verdict,
                        'expected': control['expected']['verdict'],
                        'expected_reason': control['expected']['reason'],
                        'submission_errors': issues,
                        'agrees': verdict == control['expected']['verdict'] if not issues else None,
                        'reason': reason, 'evidence_refs': refs, 'submitted_rows': rows})
    return {'submission_errors': errors, 'unmatched_rows': unmatched, 'controls': results,
            'valid_submission': not errors and all(not r['submission_errors'] for r in results),
            'all_controls_agree': not errors and all(r['agrees'] is True for r in results),
            'semantic_review': 'REQUIRED: existing citations and matching labels do not establish supported reasoning.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls', type=Path, default=DEFAULT_CONTROLS)
    parser.add_argument('--expect-controls-sha256', help='reject a changed reference source')
    parser.add_argument('--expect-packet-sha256', help='reject changed reviewer-visible inputs')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--packet', action='store_true', help='emit reviewer inputs without reference answers')
    action.add_argument('--review', type=Path, help='audit a completed review JSON file')
    args = parser.parse_args()
    try:
        suite, digest = load_controls(args.controls)
        visible_digest = packet_digest(suite)
        if args.expect_controls_sha256 and digest != args.expect_controls_sha256:
            raise ValueError('Control source identity differs from the expected SHA-256')
        if args.expect_packet_sha256 and visible_digest != args.expect_packet_sha256:
            raise ValueError('Reviewer packet identity differs from the expected SHA-256')
        if args.packet:
            print(json.dumps(packet(suite), indent=2))
            return
        raw = args.review.read_bytes()
        result = assess(suite, json.loads(raw))
        result.update(control_set=suite['id'], controls_sha256=digest, packet_sha256=visible_digest,
                      review_sha256=hashlib.sha256(raw).hexdigest())
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['all_controls_agree'] else 1)


if __name__ == '__main__':
    main()
