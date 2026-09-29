"""Check the full action-server -> Playwright MCP chain; optionally inspect a report."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'automation'))
from bridge import Bridge
from server import TOOLS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-id', help='Optional authorized report to inventory; may open the extension tab chooser')
    parser.add_argument('--compact', action='store_true', help='Check the reduced tool surface')
    args = parser.parse_args()
    bridge = Bridge(command=[sys.executable, str(ROOT / 'automation/server.py'), *(['--compact'] if args.compact else [])])
    try:
        listed = bridge.call('tools/list', {})
        names = {t['name'] for t in listed['tools']}
        assert {t['name'] for t in TOOLS} <= names
        assert {'browser_snapshot', 'browser_tabs'} <= names
        if args.compact:
            assert names - {t['name'] for t in TOOLS} == {'browser_tabs','browser_navigate','browser_snapshot','browser_take_screenshot'}
            denied = bridge.call('tools/call', {'name':'browser_run_code_unsafe', 'arguments': {'code':'async () => null'}})
            assert denied.get('isError') and 'not exposed' in denied['content'][0]['text']
        else:
            assert 'browser_run_code_unsafe' in names
        print(f'PASS: action server exposes {len(TOOLS)} Looker actions and {len(names)-len(TOOLS)} browser tools.', flush=True)
        if args.report_id:
            result = bridge.call('tools/call', {'name': 'looker_inventory', 'arguments': {'report_id': args.report_id}})
            if result.get('isError'):
                raise RuntimeError(result)
            print('PASS: read-only live report inventory through the complete stdio chain.')
    finally:
        bridge.close()


if __name__ == '__main__':
    main()
