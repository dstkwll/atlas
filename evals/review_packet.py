#!/usr/bin/env python3
"""Print a compact review packet; raw events remain authoritative."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
meta = json.loads((root / 'metadata.json').read_text())
print('# Trial', root.name)
print('Model requested:', meta['model_requested'], '/', meta['effort_requested'])
print('Host:', meta['codex_version'], '| candidate revision:', meta['revision'])
print('Task:', json.dumps(meta['case']))
print('Facts:', (root / 'result.json').read_text())
print('All completed messages/commands/edits follow. Long command outputs are explicitly clipped.')
for number, line in enumerate((root / 'events.jsonl').read_text().splitlines(), 1):
    event = json.loads(line)
    if 'sent' in event and event['sent'].get('method') == 'turn/start':
        print('EVENT', number, 'INPUT', json.dumps(event['sent']['params']['input']))
    event = event.get('received', {})
    if event.get('method') != 'item/completed':
        continue
    item = event.get('params', {}).get('item', {})
    kind = item.get('type')
    if kind == 'agentMessage':
        print('EVENT', number, 'MESSAGE', item.get('text', ''))
    elif kind == 'commandExecution':
        output = item.get('aggregatedOutput') or ''
        if len(output) > 2400:
            output = output[:1200] + '\n[CLIPPED: inspect raw event for full output]\n' + output[-1200:]
        command = item.get('command') or ''
        if len(command) > 2400:
            command = command[:1200] + '\n[CLIPPED command: inspect raw event]\n' + command[-1200:]
        print('EVENT', number, 'COMMAND', command, 'EXIT', item.get('exitCode'), '\n', output)
    elif kind == 'fileChange':
        print('EVENT', number, kind, item.get('status'), [(c.get('path'), c.get('kind')) for c in item.get('changes', [])], '(diff retained in raw event)')
    elif kind == 'contextCompaction':
        print('EVENT', number, kind, json.dumps(item))
    elif kind not in ('reasoning', 'userMessage'):
        print('EVENT', number, 'OTHER', json.dumps(item)[:2400])
result = json.loads((root / 'result.json').read_text())
for name in result.get('changed_files') or []:
    path = root / 'workspace' / name
    if path.is_file() and not path.is_symlink():
        print('\nARTIFACT', name)
        content = path.read_text(errors='replace')
        print(content if len(content) <= 24000 else content[:24000]+'\n[CLIPPED: inspect artifact directly]')

records = root / 'tool-records.jsonl'
if records.exists():
    status = root / 'tool-records-status.json'
    print('Tool capture status:', status.read_text() if status.exists() else 'not recorded by this older runner')
    print('Native tool I/O follows; retained separately from UI events.')
    for number, line in enumerate(records.read_text().splitlines(), 1):
        content = json.loads(line)
        text = json.dumps(content)
        print('TOOL RECORD', number, text if len(text) <= 4800 else text[:2400] + '[CLIPPED: inspect raw tool record]' + text[-2400:])
else:
    print('Native tool I/O was not retained in this older trial. Missing UI reads cannot establish omission.')
