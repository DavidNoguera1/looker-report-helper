"""Test MCP startup and optionally real browser actions on a local fixture."""
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Fixture(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'''<!doctype html><title>Looker helper local test</title>
<button onclick="document.getElementById('state').textContent='changed'">Change title</button>
<p id="state">original</p>
<div id="box" style="position:absolute;left:100px;top:150px;width:100px;height:60px;background:purple"
onpointerdown="this.setPointerCapture(event.pointerId);this.dataset.dragging='yes'"
onpointermove="if(this.dataset.dragging==='yes'){this.style.left=(event.clientX-50)+'px';this.style.top=(event.clientY-30)+'px'}"
onpointerup="this.dataset.dragging='no'">Chart</div>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser-test', action='store_true')
    parser.add_argument('--connect', action='store_true', help='Check the real browser extension connection without editing a report')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / '.mcp.json').read_text())['mcpServers']['looker-browser']
    command = [config['command'], *config['args']]
    if args.browser_test:
        command.remove('--extension')
        command.extend(['--headless', '--isolated'])
    # Use the actual npm launcher without a persistent cmd.exe wrapper on Windows.
    if os.name == 'nt':
        npx = Path(shutil.which(config['command']))
        command = [shutil.which('node'), str(npx.parent / 'node_modules/npm/bin/npx-cli.js'), *command[1:]]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding='utf-8')
    messages = queue.Queue()
    errors = []

    def receive():
        for line in proc.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=lambda: errors.extend(proc.stderr), daemon=True).start()
    seq = 0

    def send(value):
        proc.stdin.write(json.dumps(value) + '\n')
        proc.stdin.flush()

    def call(method, params):
        nonlocal seq
        seq += 1
        send({'jsonrpc': '2.0', 'id': seq, 'method': method, 'params': params})
        while True:
            try:
                result = messages.get(timeout=45)
            except queue.Empty:
                raise RuntimeError('MCP timed out: ' + ''.join(errors)[-1500:])
            if result.get('id') == seq:
                if 'error' in result:
                    raise RuntimeError(result['error'])
                data = result['result']
                if data.get('isError'):
                    raise RuntimeError(data)
                return data

    server = None
    try:
        init = call('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                                   'clientInfo': {'name': 'looker-helper-smoke', 'version': '1.0.0'}})
        send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        listed = call('tools/list', {})
        names = {tool['name'] for tool in listed['tools']}
        required = {'browser_navigate', 'browser_snapshot', 'browser_click',
                    'browser_take_screenshot', 'browser_mouse_drag_xy'}
        assert required <= names, f'Missing tools: {required - names}'
        print('PASS: MCP initialize and', len(names), 'tools; click, snapshot, screenshot and drag available.')
        if args.connect:
            call('tools/call', {'name': 'browser_tabs', 'arguments': {'action': 'list'}})
            print('PASS: browser extension connected; no report edited.')
        if args.browser_test:
            server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            call('tools/call', {'name': 'browser_navigate', 'arguments': {'url': f'http://127.0.0.1:{server.server_port}'}})
            call('tools/call', {'name': 'browser_mouse_click_xy', 'arguments': {'x': 50, 'y': 18}})
            call('tools/call', {'name': 'browser_evaluate', 'arguments': {'function': "() => { if(document.querySelector('#state').textContent !== 'changed') throw Error('click failed'); return 'changed'; }"}})
            call('tools/call', {'name': 'browser_mouse_drag_xy', 'arguments': {'startX': 150, 'startY': 180, 'endX': 350, 'endY': 280}})
            call('tools/call', {'name': 'browser_evaluate', 'arguments': {'function': "() => { const b = document.querySelector('#box').getBoundingClientRect(); if(Math.abs(b.x-300)>2 || Math.abs(b.y-250)>2) throw Error('drag failed: '+JSON.stringify(b)); return {x:b.x,y:b.y}; }"}})
            print('PASS: local browser navigation, button mutation and coordinate drag verified.')
            call('tools/call', {'name': 'browser_close', 'arguments': {}})
    finally:
        if server:
            server.shutdown()
            server.server_close()
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == '__main__':
    main()
