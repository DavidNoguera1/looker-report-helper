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
    args = parser.parse_args()
    bridge = Bridge(command=[sys.executable, str(ROOT / 'automation/server.py')])
    try:
        listed = bridge.call('tools/list', {})
        names = {t['name'] for t in listed['tools']}
        assert {t['name'] for t in TOOLS} <= names
        assert {'browser_run_code_unsafe', 'browser_snapshot', 'browser_tabs'} <= names
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
