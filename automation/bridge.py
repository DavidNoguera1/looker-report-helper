"""Small synchronous MCP transport. No browser credentials are read or persisted."""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


class Bridge:
    def __init__(self, endpoint=None, command=None):
        self.endpoint = endpoint
        self.session = None
        self.sequence = time.time_ns() // 1000
        self.process = None
        if endpoint is None:
            if command is None:
                spec = json.loads((ROOT / 'config/server.json').read_text(encoding='utf-8'))
                argv = ['-y', spec['package'], *spec['args']]
                npx = shutil.which('npx')
                if not npx:
                    raise RuntimeError('Install Node.js and npm/npx before starting Looker actions.')
                if os.name == 'nt':
                    npm_cli = Path(npx).parent / 'node_modules/npm/bin/npx-cli.js'
                    if not npm_cli.is_file():
                        raise RuntimeError('Cannot find npm launcher beside npx. Use a standard Node.js installation.')
                    command = [shutil.which('node'), str(npm_cli), *argv]
                else:
                    command = [npx, *argv]
            self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=None, text=True, encoding='utf-8')
            self.messages = queue.Queue()
            def receive():
                for line in self.process.stdout:
                    try:
                        self.messages.put(json.loads(line))
                    except ValueError:
                        continue
                self.messages.put({'transport_closed': True})
            threading.Thread(target=receive, daemon=True).start()
        self.call('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                               'clientInfo': {'name': 'looker-actions', 'version': '0.3.0'}})
        self.notify('notifications/initialized', {})

    def exchange(self, payload):
        if self.endpoint:
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
            if self.session:
                headers['Mcp-Session-Id'] = self.session
            request = urllib.request.Request(self.endpoint, data=json.dumps(payload).encode(), headers=headers)
            with urllib.request.urlopen(request, timeout=75) as response:
                self.session = response.headers.get('Mcp-Session-Id', self.session)
                raw = response.read().decode()
            if 'id' not in payload:
                return None
            if raw.startswith(('event:', 'data:')):
                messages = [json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
                return next(m for m in messages if m.get('id') == payload['id'])
            return json.loads(raw)
        self.process.stdin.write(json.dumps(payload) + '\n')
        self.process.stdin.flush()
        if 'id' not in payload:
            return None
        while True:
            try:
                message = self.messages.get(timeout=60)
            except queue.Empty as exc:
                raise RuntimeError('MCP response timed out. Check the extension connection and inspect the report before retrying a mutation.') from exc
            if message.get('transport_closed'):
                raise RuntimeError('Playwright MCP exited; check the server log.')
            if message.get('id') == payload['id']:
                return message

    def call(self, method, params):
        self.sequence += 1
        message = self.exchange({'jsonrpc': '2.0', 'id': self.sequence, 'method': method, 'params': params})
        if 'error' in message:
            raise RuntimeError(message['error'])
        return message['result']

    def notify(self, method, params):
        self.exchange({'jsonrpc': '2.0', 'method': method, 'params': params})

    def close(self):
        if self.process:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=5)
