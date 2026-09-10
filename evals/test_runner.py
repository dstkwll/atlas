"""Failure paths that must retain evidence rather than report success."""
import argparse
import io
import json
from pathlib import Path
import queue
import tempfile
import unittest
from unittest.mock import Mock, patch
import run


class OpenBuffer(io.StringIO):
    def close(self):
        self.flush()


class RunnerFailures(unittest.TestCase):
    def test_tail_event_is_retained_and_live_reader_is_rejected(self):
        host = run.Host.__new__(run.Host)
        host.process = Mock(pid=999999)
        host.reader = Mock()
        host.reader.is_alive.return_value = False
        host.queue = queue.Queue()
        host.queue.put({'method': 'tail-notification'})
        host.events = []
        host.log, host.stderr = OpenBuffer(), OpenBuffer()
        with patch('run.os.killpg'):
            host.close()
        self.assertIn('tail-notification', host.log.getvalue())
        host.reader.is_alive.return_value = True
        with patch('run.os.killpg'), self.assertRaisesRegex(RuntimeError, 'capture did not terminate'):
            host.close()

    def test_termination_error_still_retains_tail(self):
        host=run.Host.__new__(run.Host)
        host.process=Mock(pid=999999); host.reader=Mock()
        host.queue=queue.Queue(); host.queue.put({'method':'tail-after-error'})
        host.events=[]; host.log=OpenBuffer(); host.stderr=OpenBuffer()
        with patch('run.os.killpg',side_effect=PermissionError('denied')), self.assertRaises(PermissionError):
            host.close()
        self.assertIn('tail-after-error',host.log.getvalue())

    def test_partial_tool_capture_is_explicit_and_excludes_reasoning(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); home=root/'home'; home.mkdir(); out=root/'out'; out.mkdir()
            (home/'rollout-test.jsonl').write_text(
                json.dumps({'type':'response_item','payload':{'type':'function_call','name':'exec','arguments':'read'}})+'\n'+
                json.dumps({'type':'response_item','payload':{'type':'reasoning','content':'private reasoning'}})+'\n'+
                '{"type":')
            status=run.capture_tools(home,out)
            self.assertFalse(status['parsed_without_errors'])
            self.assertEqual(status['records'],1)
            text=(out/'tool-records.jsonl').read_text()
            self.assertIn('read',text); self.assertNotIn('private reasoning',text)

    def test_no_turn_and_checker_failure_retain_both_errors(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); auth=root/'auth'; auth.mkdir(); (auth/'auth.json').write_text('{}')
            args=argparse.Namespace(model='test',effort='low',timeout=1,auth_home=auth)
            case={'id':'fixture','check':'unchanged','turns':['Hello'],'no_edit_before':1}
            with patch('run.Host',side_effect=RuntimeError('host failed')), patch('run.check',side_effect=OSError('checker failed')), patch('run.subprocess.check_output',return_value='test\n'):
                self.assertFalse(run.trial(case,args,root/'output'))
            result=json.loads((root/'output/result.json').read_text())
            self.assertIn('host failed',result['error']); self.assertIn('checker failed',result['error'])
            self.assertIsNone(result['facts']['first_turn_workspace_matches_before'])

    def test_teardown_failure_is_blocked_and_retained(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            auth = root/'auth'; auth.mkdir(); (auth/'auth.json').write_text('{}')
            args = argparse.Namespace(model='test', effort='low', timeout=1, auth_home=auth)
            host = Mock()
            host.events = []
            host.request.side_effect = [{}, {'thread': {'id': 'thread'}}, {'turn': {'id': 'turn'}}]
            host.wait.return_value = {'params': {'turn': {'id': 'turn', 'status': 'completed'}}}
            host.process.pid = 999999
            host.process.poll.return_value = 0
            host.close.side_effect = OSError('teardown failure')
            with patch('run.Host', return_value=host), patch('run.subprocess.check_output', return_value='test\n'):
                ok = run.trial({'id':'fixture','check':'unchanged','turns':['Hello']},args,root/'output')
            result=json.loads((root/'output/result.json').read_text())
            self.assertFalse(ok)
            self.assertEqual(result['status'],'blocked')
            self.assertFalse(result['facts']['host_completed'])
            self.assertIn('teardown failure',result['error'])
            self.assertTrue(result['cleanup']['temporary_home_removed'])


if __name__ == '__main__': unittest.main()
