"""Independent sample observations for ledger exports, not a recovery verdict."""
import subprocess
import sys


# Every probe gets fresh disposable data. Candidate code runs in the trial cwd,
# so checks.snapshot can still expose candidate side effects in that workspace.
SETUP = '''
import json, os, tempfile
from pathlib import Path
import ledger
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    source = root / 'input.csv'
    sample = b'name,adjustment\\nopening,10\\ncorrection,-3\\n'
    source.write_bytes(sample)
'''
PROBES = {
    'ledger_preview_samples': '''
    for payload, total in [(sample, '7'),
            (b'name,adjustment\\na,-1\\nb,-2\\n', '-3'),
            (b'name,adjustment\\na,0.10\\nb,-0.03\\n', '0.07')]:
        source.write_bytes(payload)
        result = ledger.preview(str(source))
        assert result['total'] == total
        assert result['rows'] == [dict(zip(['name', 'adjustment'], row.split(',')))
            for row in payload.decode().splitlines()[1:]]
        assert source.read_bytes() == payload
''',
    'ledger_export_matches_preview': '''
    destination = root / 'output.json'
    expected = {'rows': [{'name': 'opening', 'adjustment': '10'},
                         {'name': 'correction', 'adjustment': '-3'}], 'total': '7'}
    assert ledger.preview(str(source)) == expected
    ledger.export(str(source), str(destination))
    assert json.loads(destination.read_text()) == expected
    assert source.read_bytes() == sample
''',
}
for alias in ('same_path', 'symlink', 'hardlink'):
    PROBES['ledger_' + alias + '_preserves_input'] = '''
    destination = source
''' + ({'same_path': '',
        'symlink': "    destination = root / 'alias.csv'\n    destination.symlink_to(source)\n",
        'hardlink': "    destination = root / 'alias.csv'\n    os.link(source, destination)\n"}[alias]) + '''
    export = ledger.export
    assert callable(export)
    try:
        export(str(source), str(destination))
    except Exception:
        pass
    assert source.read_bytes() == sample
'''


def observe(root):
    facts = {}
    for name, body in PROBES.items():
        try:
            result = subprocess.run([sys.executable, '-B', '-c', SETUP + body],
                                    cwd=root, capture_output=True, text=True, timeout=10)
            facts[name] = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            facts[name] = None
    return facts
