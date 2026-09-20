#!/usr/bin/env python3
"""Prepare matched review packets and record endpoint facts; never launch agents."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from checks import snapshot

ROOT = Path(__file__).resolve().parent.parent
CONDITIONS = ('direct', 'briefed', 'defined')
SCENARIOS = ('regression', 'control', 'uncertain')
RUNBOOKS = ('independent-review.md', 'failure-handling.md')

CONTRACT = '''Own a read-only failure-handling review of candidate.py against requirements.md.
Inspect the actual sources, provider.py and caller.py; do not rely on a producer's narrative.
Use guidance/references/independent-review.md and guidance/references/failure-handling.md.
Return prioritized, actionable findings with location, triggering condition, observed or
reasoned consequence, evidence and uncertainty. Distinguish defects from unresolved
requirements and optional improvements. A supported zero-finding result is valid.
Do not repair code, make product-policy decisions, contact external services, install
software, inspect other projects or launch further workers. Local Python probes are
permitted with -B; use in-memory inputs and do not write source or test files.
Report runbooks actually used and checks actually performed. No finding quota.
'''

REQUIREMENTS = '''# Delivery review

Review the candidate for a bounded local delivery operation before integration.
The operation may send at most twice. A transport timeout may occur after the
provider has committed. Preserve the single logical operation: retrying must not
create another effect. The caller must not report completion for a rejected or
unknown result. Provider rejection may be returned as an explicit rejected status.
Use the documented provider contract; don't infer a missing production guarantee
from the fake provider alone. Code repair, deployment and external calls are out
of scope. Caller-level deadlines already bound the real transport; these local
fakes do not model wall-clock cancellation. No additional per-function deadline
is required by this review assignment.
'''

PROVIDER = '''"""Provider contract: keys deduplicate for the entire operation, including retries.
A cached committed response is authoritative. Rejection creates no effect.
"""
class Provider:
    def __init__(self, mode="normal"):
        self.mode = mode
        self.effects = []
        self.cached = {}
        self.calls = 0

    def send(self, key, payload):
        self.calls += 1
        if key in self.cached:
            return self.cached[key]
        if self.mode == "reject":
            return {"committed": False, "reason": "rejected"}
        if self.mode == "unavailable":
            raise TimeoutError("unknown outcome")
        self.effects.append(payload)
        reply = {"committed": True, "receipt": len(self.effects)}
        self.cached[key] = reply
        if self.mode == "lost_ack" and self.calls == 1:
            raise TimeoutError("ack lost after commit")
        return reply
'''

CANDIDATE = '''from uuid import uuid4


def deliver(provider, payload):
    key = str(uuid4())
    for attempt in range(2):
        try:
            reply = provider.send(key, payload)
        except TimeoutError:
            continue
        if reply["committed"]:
            return {"status": "complete", "receipt": reply["receipt"]}
        return {"status": "rejected"}
    return {"status": "unknown"}
'''

CALLER = '''from candidate import deliver


def run(provider, payload):
    result = deliver(provider, payload)
    # The real adapter applies an overall deadline before this call.
    return result["status"] == "complete"
'''


def fixture(scenario):
    candidate, provider = CANDIDATE, PROVIDER
    if scenario == 'regression':
        candidate = candidate.replace('    key = str(uuid4())\n', '').replace(
            'provider.send(key, payload)', 'provider.send(str(uuid4()), payload)').replace(
            'if reply["committed"]:', 'if reply:').replace(
            'reply["receipt"]}', 'reply.get("receipt")}')
    elif scenario == 'uncertain':
        provider = provider.replace(
            'keys deduplicate for the entire operation, including retries.',
            'production deduplication retention is unspecified.\n'
            'This fake caches keys indefinitely; production may not. Confirm retention\n'
            'before relying on it after an unknown write outcome.')
    elif scenario != 'control':
        raise ValueError('unknown scenario')
    return {'requirements.md': REQUIREMENTS, 'candidate.py': candidate,
            'provider.py': provider, 'caller.py': CALLER}


def task(condition):
    common = '''Act as a fresh Atlas lead on this review assignment. Read guidance/SKILL.md
and AGENTS.md, then the assignment below. You did not produce the candidate.
Use the current parent model and reasoning settings without override. Stay in
this packet's workspace. The operator gives the entire trial (lead plus worker)
180 seconds and at most one worker. Stop with explicit uncertainty if the bound
is reached. No follow-up worker or repair round. This is an effort ceiling, not
a requirement to use all the time. The operator must monitor actual elapsed time.
Write your final integrated review to results/review.md and explain actual
delegation, guide use, checks and unverified claims in your final message.
Do not read the evaluator, sibling packets, schedule or grading rubric.

Assignment contract:
'''
    if condition == 'direct':
        method = '\nApply this contract yourself. Do not delegate.\n'
    elif condition == 'briefed':
        method = '''
Delegate exactly one fresh-context worker. Give it the verbatim assignment
contract above and this absolute workspace path. Do not send prior conversation,
your own initial findings or evaluation material. Inspect its returned evidence
and relevant source before writing your integrated review. Preserve the worker's
return unchanged in results/worker.md and record its actual session identifier.
'''
    elif condition == 'defined':
        method = '''
Delegate exactly one fresh-context worker as the predefined failure reviewer.
Give it this absolute workspace path and instruct it to read roles/failure-reviewer.md
as its assignment contract. Do not send prior conversation, your own initial
findings or evaluation material. Inspect its returned evidence and relevant source
before writing your integrated review. Preserve the worker's return unchanged in
results/worker.md and record its actual session identifier.
'''
    else:
        raise ValueError('unknown condition')
    return common + CONTRACT + method


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    schedule = []
    for s, scenario in enumerate(SCENARIOS):
        # Rotate order to avoid always starting with one condition. One trial/cell.
        for j in range(3):
            condition = CONDITIONS[(s + j) % 3]
            label = f'trial-{len(schedule) + 1:02}'
            trial = output / label
            workspace = trial / 'workspace'
            workspace.mkdir(parents=True)
            for name, content in fixture(scenario).items():
                (workspace / name).write_text(content)
            guidance = workspace / 'guidance'
            shutil.copytree(ROOT / 'plugins/atlas/skills/atlas', guidance)
            (workspace / 'roles').mkdir()
            # Same information available in every condition; only invocation varies.
            (workspace / 'roles/failure-reviewer.md').write_text(CONTRACT)
            (workspace / 'results').mkdir()
            (workspace / 'AGENTS.md').write_text(
                'Use only this workspace. Review source is read-only; only results/ may be written. '
                'Do not read sibling trials, evaluator files, external services or user-profile files. '
                'Do not install software. Local Python probes must use -B and in-memory inputs. '
                'The assigned lead may launch the one worker explicitly required by task.md; '
                'workers may not delegate. The lead owns integration. Results are evidence, '
                'not authorization to repair or publish. These are instructions, not a security sandbox.\n')
            (workspace / 'task.md').write_text(task(condition))
            (trial / 'before.json').write_text(json.dumps(snapshot(workspace), indent=2))
            schedule.append({'trial': label, 'scenario': scenario, 'condition': condition})
    manifest = {'revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'guidance_files': snapshot(ROOT / 'plugins/atlas/skills/atlas'),
        'evaluator_files': snapshot(ROOT / 'evals'),
        'seconds_per_trial': 180, 'trials_per_cell': 1, 'schedule': schedule,
        'host': None, 'model': None, 'effort': None,
        'note': 'Operator must record actual host/settings and execution evidence; preparation is not a run.'}
    (output / 'schedule.json').write_text(json.dumps(manifest, indent=2))
    return manifest


def observe(trial):
    workspace = trial / 'workspace'
    before = json.loads((trial / 'before.json').read_text())
    after = snapshot(workspace)
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    review = workspace / 'results/review.md'
    # No execution, grading of words, or trust in self-reported worker identity.
    return {'changed_files': changed,
            'facts': {'only_results_changed_in_observed_paths': all(p.startswith('results/') for p in changed),
                      'review_nonempty_regular_file': review.is_file() and not review.is_symlink()
                      and review.stat().st_size > 0},
            'behavior_verdict': 'UNREVIEWED', 'routing_verdict': 'UNREVIEWED',
            'worker_execution': 'UNVERIFIED', 'host_completion': 'UNVERIFIED',
            'token_usage': None, 'monetary_cost': None,
            'limitations': 'Endpoint snapshot only; .git and __pycache__ are excluded. '
            'No proof of transient effects or out-of-workspace access.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare').add_argument('--output', type=Path, required=True)
    sub.add_parser('observe').add_argument('trial', type=Path)
    args = parser.parse_args()
    result = prepare(args.output.resolve()) if args.command == 'prepare' else observe(args.trial.resolve())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
