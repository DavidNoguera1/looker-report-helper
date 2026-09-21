"""Boundary tests: reject unsafe/invalid plans before touching a browser."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'automation'))
from server import validate, TOOLS, execute


class ActionTests(unittest.TestCase):
    def test_invalid_arguments_never_reach_browser(self):
        class NeverCall:
            def call(self, *args):
                raise AssertionError('Invalid input reached browser')
        base = {'report_id': 'sample-report', 'type': 'table', 'x': 20, 'y': 20, 'width': 400, 'height': 250}
        for change in [{'report_id': 'a/../../wrong'}, {'width': -1}, {'x': True},
                       {'x': 1.5}, {'type': 'unsupported'}, {'arbitrary_script': 'alert(1)'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                execute(NeverCall(), 'looker_create', {**base, **change})
        with self.assertRaises(ValueError):
            validate('looker_layout', {'report_id': 'sample-report', 'component_id': 'cd-x,body'})

    def test_user_text_is_data_and_output_is_concise(self):
        class Capture:
            def call(self, method, params):
                self.code = params['arguments']['code']
                return {'content': [{'type': 'text', 'text': '### Result\n{}\n### Ran Playwright code\nlarge source'}]}
        bridge = Capture()
        text = 'Quotes " and \\ slashes; </script>\nUnicode: \u00f1'
        args = {'report_id': 'sample-report', 'component_id': 'cd-example', 'title': text}
        result = execute(bridge, 'looker_set_title', args)
        self.assertIn(json.dumps({'action': 'set_title', **args}, ensure_ascii=True), bridge.code)
        self.assertNotIn('large source', result['content'][0]['text'])

    def test_protocol_without_browser(self):
        requests = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'ping'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'unknown'},
        ]
        run = subprocess.run([sys.executable, str(ROOT / 'automation/server.py')],
                             input=''.join(json.dumps(r)+'\n' for r in requests),
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        responses = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([r['id'] for r in responses], [1, 2, 3])
        self.assertIn('tools', responses[0]['result']['capabilities'])
        self.assertEqual(responses[2]['error']['code'], -32601)

    def test_schemas_do_not_require_optional_index(self):
        args = {'report_id': 'sample-report', 'component_id': 'cd-example', 'slot': 'metric', 'field': 'Total'}
        self.assertEqual(validate('looker_set_field', args)['action'], 'set_field')
        names = [t['name'] for t in TOOLS]
        self.assertEqual(len(names), len(set(names)))


if __name__ == '__main__':
    unittest.main()
