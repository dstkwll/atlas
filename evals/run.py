#!/usr/bin/env python3
"""Bounded native Codex trials. Requires existing local Codex authentication."""
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import subprocess
import tempfile
import threading
import time

from checks import check, snapshot
from fixtures import FIXTURES

ROOT = Path(__file__).resolve().parent.parent


class Host:
    def __init__(self, home, workspace, output, deadline):
        self.deadline, self.sequence, self.events = deadline, 0, []
        self.queue = queue.Queue()
        self.log = (output / 'events.jsonl').open('w')
        self.stderr = (output / 'host.stderr').open('w')
        env = os.environ.copy()
        env['CODEX_HOME'] = str(home)
        self.process = subprocess.Popen(['codex', 'app-server', '--listen', 'stdio://'],
            cwd=workspace, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.stderr, text=True, bufsize=1, start_new_session=True)
        def read():
            for line in self.process.stdout:
                try:
                    self.queue.put(json.loads(line))
                except ValueError:
                    self.queue.put({'invalid_json': line})
            self.queue.put({'host_exited': True})
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def send(self, payload):
        self.log.write(json.dumps({'sent': payload}) + '\n')
        self.log.flush()
        self.process.stdin.write(json.dumps(payload) + '\n')
        self.process.stdin.flush()

    def wait(self, predicate, start=0):
        for event in self.events[start:]:
            if predicate(event):
                return event
        while True:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Trial deadline exceeded')
            try:
                event = self.queue.get(timeout=min(remaining, 30))
            except queue.Empty:
                continue
            self.events.append(event)
            self.log.write(json.dumps({'received': event}) + '\n')
            self.log.flush()
            if 'host_exited' in event or 'invalid_json' in event:
                raise RuntimeError(str(event))
            if 'id' in event and 'method' in event:
                # No implicit approvals or simulated user decisions.
                self.send({'id': event['id'], 'error': {'code': -32603,
                    'message': 'Unexpected interaction: bounded trial supplies no extra authority'}})
            if predicate(event):
                return event

    def request(self, method, params):
        self.sequence += 1
        request_id = self.sequence
        mark = len(self.events)
        self.send({'id': request_id, 'method': method, 'params': params})
        response = self.wait(lambda e: e.get('id') == request_id and 'method' not in e, mark)
        if 'error' in response:
            raise RuntimeError(str(response['error']))
        return response['result']

    def close(self):
        # Terminate only this trial's process group; always retain queued evidence.
        try:
            try:
                os.killpg(self.process.pid, signal.SIGTERM)
                self.process.wait(timeout=5)
            except ProcessLookupError:
                pass
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=5)
        finally:
            self.reader.join(timeout=2)
            while not self.queue.empty():
                event = self.queue.get_nowait()
                self.events.append(event)
                self.log.write(json.dumps({'received': event}) + '\n')
            self.log.close()
            self.stderr.close()
        if self.reader.is_alive():
            raise RuntimeError('Host stdout capture did not terminate; tail evidence may be incomplete')


def capture_tools(home, output):
    """Retain tool I/O without reasoning/instructions; parsing health is explicit."""
    status = {'rollouts': 0, 'records': 0, 'errors': []}
    try:
        with (output / 'tool-records.jsonl').open('w') as records:
            for path in sorted(home.rglob('rollout-*.jsonl')):
                status['rollouts'] += 1
                for n, line in enumerate(path.read_bytes().splitlines(), 1):
                    try:
                        entry = json.loads(line)
                        payload = entry.get('payload', {})
                        if entry.get('type') == 'response_item' and payload.get('type') in (
                                'function_call', 'function_call_output', 'custom_tool_call', 'custom_tool_call_output'):
                            records.write(json.dumps(payload) + '\n')
                            status['records'] += 1
                    except (ValueError, AttributeError):
                        # Do not save malformed raw lines: they could be reasoning or instructions.
                        status['errors'].append(f'{path.name}:{n}: invalid record')
    except OSError as exc:
        status['errors'].append(str(exc))
    status['parsed_without_errors'] = bool(status['rollouts']) and not status['errors']
    (output / 'tool-records-status.json').write_text(json.dumps(status, indent=2))
    return status


def trial(case, args, output):
    output.mkdir(parents=True, exist_ok=False)
    workspace = output / 'workspace'
    workspace.mkdir()
    for name, content in FIXTURES.get(case.get('fixture'), {}).items():
        (workspace / name).parent.mkdir(parents=True, exist_ok=True)
        (workspace / name).write_text(content)
    skills = workspace / '.agents/skills'
    shutil.copytree(ROOT / 'plugins/atlas/skills', skills)
    if case.get('missing'):
        shutil.rmtree(skills / 'atlas')
    (workspace / 'AGENTS.md').write_text(
        'This is a disposable local project. Use only local project files and tools. '
        'Do not contact external services, delegate, install software, read other projects '
        'or user-profile guidance, or change the installed .agents/skills or this file. '
        'Use only the project-local skill installation. Planning files belong under planning/.\n')
    before = snapshot(workspace)
    (output / 'before.json').write_text(json.dumps(before, indent=2))
    metadata = {'case': case, 'model_requested': args.model, 'effort_requested': args.effort,
        'codex_version': subprocess.check_output(['codex', '--version'], text=True).strip(),
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'candidate_files': snapshot(ROOT / 'plugins/atlas/skills'), 'timeout_seconds': args.timeout,
        'protocol': 'native Codex app-server', 'runner_files': snapshot(ROOT / 'evals'), 'activation': 'explicit project-local skill input',
        'started': time.time()}
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    completed, host, home, error, turns = False, None, None, None, []
    try:
        # Separate configuration, skills and session state. Credentials never enter evidence.
        with tempfile.TemporaryDirectory(prefix='atlas-eval-home-') as directory:
            home = Path(directory)
            auth = args.auth_home / 'auth.json'
            if not auth.is_file():
                raise RuntimeError('No file-based Codex authentication at --auth-home; no login attempted')
            shutil.copy2(auth, home / 'auth.json')
            os.chmod(home / 'auth.json', 0o600)
            (home / 'config.toml').write_text('web_search = "disabled"\n')
            try:
                host = Host(home, workspace, output, time.monotonic() + args.timeout)
                init = host.request('initialize', {'clientInfo': {'name': 'atlas_eval', 'version': '1'},
                    'capabilities': {'experimentalApi': True}})
                host.send({'method': 'initialized', 'params': {}})
                thread = host.request('thread/start', {'model': args.model, 'cwd': str(workspace),
                    'approvalPolicy': 'never', 'sandbox': 'workspace-write', 'ephemeral': False,
                    'config': {'model_reasoning_effort': args.effort}})
                tid = thread['thread']['id']
                metadata.update({'initialize': init, 'thread': thread, 'isolated_home': str(home), 'host_pid': host.process.pid})
                (output / 'metadata.json').write_text(json.dumps(metadata, indent=2))
                for i, prompt in enumerate(case['turns']):
                    if i == case.get('compact_before'):
                        mark = len(host.events)
                        host.request('thread/compact/start', {'threadId': tid})
                        host.wait(lambda e: e.get('method') == 'item/completed'
                            and e.get('params', {}).get('item', {}).get('type') == 'contextCompaction', mark)
                        # Wait for the compaction turn to finish before the next ordinary turn.
                        host.wait(lambda e: e.get('method') == 'turn/completed', mark)
                    inputs = [{'type': 'text', 'text': prompt}]
                    if i == 0:
                        entry = case.get('entry', 'atlas')
                        inputs.insert(0, {'type': 'skill', 'name': entry,
                            'path': str(skills / entry / 'SKILL.md')})
                    mark = len(host.events)
                    response = host.request('turn/start', {'threadId': tid, 'input': inputs, 'effort': args.effort})
                    turn_id = response['turn']['id']
                    done = host.wait(lambda e: e.get('method') == 'turn/completed'
                        and e.get('params', {}).get('turn', {}).get('id') == turn_id, mark)
                    state = done['params']['turn']
                    turns.append({'turn': i, 'status': state['status'], 'files': snapshot(workspace)})
                    (output / 'turns.json').write_text(json.dumps(turns, indent=2))
                    print(case['id'], 'turn', i + 1, state['status'], flush=True)
                    if state['status'] != 'completed':
                        raise RuntimeError('Native turn failed: ' + json.dumps(state))
                completed = True
            finally:
                if host:
                    try:
                        host.close()
                    finally:
                        try:
                            capture_tools(home, output)
                        except OSError as exc:
                            # Preserve an existing turn/teardown failure if recording itself fails.
                            completed = False
                            error = '; '.join(x for x in (error, 'Tool capture failed: ' + str(exc)) if x)

    except Exception as exc:
        completed, error = False, '; '.join(x for x in (error, str(exc)) if x)
    try:
        result = check(case, workspace, before, completed)
    except Exception as exc:
        completed, error = False, '; '.join(x for x in (error, 'Checker failed: ' + str(exc)) if x)
        result = {'facts': {'host_completed': False}, 'changed_files': None, 'probe_changes': None, 'behavior_verdict': 'UNKNOWN', 'routing_verdict': 'UNREVIEWED'}
    if case.get('no_edit_before'):
        result['facts']['first_turn_workspace_matches_before'] = (turns[0]['files'] == before) if turns else None
    result.update({'cleanup': {'host_stopped': host.process.poll() is not None if host else None, 'temporary_home_removed': not home.exists() if home else None}, 'error': error, 'elapsed_seconds': round(time.time() - metadata['started'], 1),
                   'status': 'completed' if completed else 'blocked', 'case': case['id']})
    (output / 'result.json').write_text(json.dumps(result, indent=2))
    try:
        (output / 'after.json').write_text(json.dumps(snapshot(workspace), indent=2))
    except OSError as exc:
        (output / 'snapshot-error.txt').write_text(str(exc))
    print(json.dumps(result), flush=True)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', required=True, help='case id; repeat flag to select several')
    parser.add_argument('--repeat', type=int, choices=range(1, 4), default=1)
    parser.add_argument('--model', required=True)
    parser.add_argument('--effort', choices=['low', 'medium', 'high'], default='low')
    parser.add_argument('--timeout', type=int, default=300, help='total native-host seconds per trial')
    parser.add_argument('--output', type=Path, required=True, help='new local evidence directory; never commit raw runs')
    parser.add_argument('--auth-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')))
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 600:
        parser.error('--timeout must be between 1 and 600 seconds')
    cases = json.loads((ROOT / 'evals/cases.json').read_text())
    if set(args.case) - {c['id'] for c in cases}:
        parser.error('unknown case id')
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    ok = True
    for case in cases:
        if case['id'] in args.case:
            for n in range(args.repeat):
                ok = trial(case, args, args.output / f"{case['id']}-{n+1}") and ok
    raise SystemExit(0 if ok else 2)  # Host completion only, never a behavior pass.


if __name__ == '__main__':
    main()
