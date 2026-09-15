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
    def test_nested_fixture_seeding_precedes_host_start(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); auth = root/'auth'; auth.mkdir()
            (auth/'auth.json').write_text('{}')
            args = argparse.Namespace(model='test', effort='low', timeout=1, auth_home=auth)
            case = {'id':'seeded-reader','fixture':'seeded-reader','check':'unchanged','turns':['Read the recipe']}
            fixture = {'planning/station/recipe.md':'Run the existing boundary assertion.\n'}
            with patch.dict(run.FIXTURES, {'seeded-reader':fixture}), patch('run.Host', side_effect=RuntimeError('host unavailable')), patch('run.subprocess.check_output', return_value='test\n'):
                self.assertFalse(run.trial(case, args, root/'output'))
            self.assertEqual((root/'output/workspace/planning/station/recipe.md').read_text(), fixture['planning/station/recipe.md'])
            before = json.loads((root/'output/before.json').read_text())
            self.assertIn('planning/station/recipe.md', before)

    def test_fresh_recovery_uses_new_thread_and_only_current_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); auth=root/'auth'; auth.mkdir(); (auth/'auth.json').write_text('{}')
            args=argparse.Namespace(model='test',effort='low',timeout=1,auth_home=auth)
            host=Mock(); host.events=[]; host.process.pid=999999; host.process.poll.return_value=0
            host.request.side_effect=[{}, {'thread':{'id':'old'}}, {'turn':{'id':'one'}}, {'thread':{'id':'new'}}, {'turn':{'id':'two'}}]
            host.wait.side_effect=[{'params':{'turn':{'id':'one','status':'completed'}}}, {'params':{'turn':{'id':'two','status':'completed'}}}]
            with patch('run.Host',return_value=host), patch('run.subprocess.check_output',return_value='test\n'):
                self.assertTrue(run.trial({'id':'fresh','check':'unchanged','turns':['private prior dialogue','Recover from files'],'fresh_thread_before':1},args,root/'output'))
            calls=[c for c in host.request.call_args_list if c.args[0]=='turn/start']
            self.assertEqual(calls[1].args[1]['threadId'],'new')
            self.assertEqual(calls[1].args[1]['input'], [
                {'type':'skill','name':'atlas','path':str(root/'output/workspace/.agents/skills/atlas/SKILL.md')},
                {'type':'text','text':'Recover from files'}])
            starts=[c for c in host.request.call_args_list if c.args[0]=='thread/start']
            self.assertEqual(len(starts),2)
            self.assertEqual(starts[0].args[1]['cwd'],str(root/'output/workspace'))
            self.assertEqual(starts[1].args[1]['cwd'],starts[0].args[1]['cwd'])
            meta=json.loads((root/'output/metadata.json').read_text())
            self.assertEqual(meta['fresh_thread'], {'previous_id':'old','id':'new','before_turn':1})

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
