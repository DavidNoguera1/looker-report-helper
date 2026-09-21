"""Print a client configuration; never modify the user's configuration files."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def render(client, platform, with_actions=False):
    spec = json.loads((ROOT / 'config/server.json').read_text(encoding='utf-8'))
    args = ['-y', spec['package'], *spec['args']]
    command = 'npx'
    if platform == 'windows':
        if client == 'codex':
            command = 'npx.cmd'
        else:
            command, args = 'cmd', ['/c', 'npx', *args]
    if with_actions:
        # Generated locally after cloning. Never commit this machine-specific output.
        command, args = sys.executable, [str(ROOT / 'automation/server.py')]
        if platform == 'windows':
            # Windows Store Python aliases can fail when spawned directly by Bun/OpenCode.
            command, args = 'cmd', ['/c', 'python', str(ROOT / 'automation/server.py')]
    if client == 'codex':
        return ('[mcp_servers.looker-browser]\n'
                f'command = {json.dumps(command)}\n'
                f'args = {json.dumps(args)}\nstartup_timeout_sec = 60\n')
    if client == 'opencode':
        result = {'$schema': 'https://opencode.ai/config.json', 'mcp': {
            'looker-browser': {'type': 'local', 'command': [command, *args],
                               'enabled': True, 'timeout': 60000}}}
    else:
        result = {'mcpServers': {'looker-browser': {'command': command, 'args': args}}}
    return json.dumps(result, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=['codex', 'claude', 'opencode', 'plugin'], required=True)
    parser.add_argument('--platform', choices=['windows', 'posix'], required=True)
    parser.add_argument('--with-actions', action='store_true', help='Use the local Looker action server (includes browser tools)')
    args = parser.parse_args()
    print(render(args.client, args.platform, args.with_actions), end='')


if __name__ == '__main__':
    main()
