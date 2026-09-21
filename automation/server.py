"""Serve deterministic Looker UI actions plus the official Playwright tools over MCP."""
import argparse
import json
import re
import sys
from bridge import Bridge, ROOT

STRING = {'type': 'string', 'minLength': 1, 'maxLength': 200}
REPORT = {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{1,100}$'}
COMPONENT = {'type': 'string', 'pattern': '^cd-[A-Za-z0-9_-]{1,100}$'}
GEOMETRY = {k: {'type': 'integer', 'minimum': 0 if k in ('x', 'y') else 20, 'maximum': 4000}
            for k in ('x', 'y', 'width', 'height')}


def tool(name, description, properties, required=None, readonly=False):
    properties = {'report_id': REPORT, **properties}
    return {'name': 'looker_' + name, 'description': description,
            'inputSchema': {'type': 'object', 'properties': properties,
                            'required': ['report_id', *(required if required is not None else [key for key in properties if key != 'report_id'])],
                            'additionalProperties': False},
            'annotations': {'readOnlyHint': readonly, 'destructiveHint': False,
                            'idempotentHint': name in ('inventory', 'layout', 'set_field', 'set_title')}}


TOOLS = [
    tool('inventory', 'Read chart IDs, titles and canvas-coordinate rectangles on the current report page. No mutation.', {}, readonly=True),
    tool('inspect', 'Select one chart and read its source and field slots. Use the ID from inventory.', {'component_id': COMPONENT}),
    tool('create', 'Insert one chart at x/y/width/height in canvas pixels. Uses the current default source and fields. Returns the new ID. Never blindly retry after timeout; inventory first.',
         {'type': {'type': 'string', 'enum': ['table', 'scorecard', 'bar', 'pie', 'time_series', 'pivot']}, **GEOMETRY}),
    tool('layout', 'Move and resize one existing chart to exact canvas coordinates; verify geometry. Supports freeform layout only.',
         {'component_id': COMPONENT, **GEOMETRY}),
    tool('set_field', 'Replace one existing field slot with an exact source field name. Does not add fields or set aggregation. Inspect first.',
         {'component_id': COMPONENT, 'slot': {'type': 'string', 'enum': ['metric', 'dimension', 'pivot_row', 'pivot_column']},
          'index': {'type': 'integer', 'minimum': 0, 'maximum': 20}, 'field': STRING}, ['component_id', 'slot', 'field']),
    tool('set_title', 'Enable the chart title, set its text and verify it on the canvas.', {'component_id': COMPONENT, 'title': STRING}),
    tool('set_sort', 'Set the primary sort field and direction on a table, bar or pie chart. Verify rendered ordering separately; this checks controls.',
         {'component_id': COMPONENT, 'field': STRING, 'direction': {'type': 'string', 'enum': ['ascending', 'descending']}}),
]


def validate(name, arguments):
    definition = next((t for t in TOOLS if t['name'] == name), None)
    if definition is None:
        raise ValueError('Unknown Looker action')
    schema = definition['inputSchema']
    if not isinstance(arguments, dict) or set(arguments) - schema['properties'].keys():
        raise ValueError('Unexpected arguments')
    for key in schema['required']:
        if key not in arguments:
            raise ValueError('Missing argument: ' + key)
    for key, value in arguments.items():
        field = schema['properties'][key]
        if field['type'] == 'integer':
            if type(value) is not int or not field['minimum'] <= value <= field['maximum']:
                raise ValueError('Invalid integer: ' + key)
        elif not isinstance(value, str) or not value or len(value) > field.get('maxLength', 200):
            raise ValueError('Invalid string: ' + key)
        if 'enum' in field and value not in field['enum']:
            raise ValueError('Invalid choice: ' + key)
        if 'pattern' in field and re.fullmatch(field['pattern'], value) is None:
            raise ValueError('Invalid identifier: ' + key)
    return {'action': name.removeprefix('looker_'), **arguments}


def execute(bridge, name, arguments):
    args = validate(name, arguments)
    source = (ROOT / 'automation/looker.js').read_text(encoding='utf-8')
    code = 'async (page) => {\n' + source + '\nreturn await lookerAction(page, ' + json.dumps(args, ensure_ascii=True) + ');\n}'
    result = bridge.call('tools/call', {'name': 'browser_run_code_unsafe', 'arguments': {'code': code}})
    # Keep deterministic tools concise. The underlying tool echoes its entire program.
    for item in result.get('content', []):
        if item.get('type') == 'text':
            item['text'] = item['text'].split('\n### Ran Playwright code')[0]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', help='Development only: existing local Playwright MCP HTTP endpoint')
    parser.add_argument('--call', choices=[t['name'] for t in TOOLS], help='Run one action with JSON arguments from stdin')
    args = parser.parse_args()
    if args.endpoint and not re.fullmatch(r'http://(?:localhost|127\.0\.0\.1):\d+/mcp', args.endpoint):
        parser.error('Only loopback HTTP endpoints are supported')
    sys.stdout.reconfigure(encoding='utf-8')
    bridge = None
    try:
        if args.call:
            arguments = json.load(sys.stdin)
            validate(args.call, arguments)
            bridge = Bridge(args.endpoint)
            result = execute(bridge, args.call, arguments)
            print(json.dumps(result, ensure_ascii=False))
            return 1 if result.get('isError') else 0
        for line in sys.stdin:
            request = None
            try:
                request = json.loads(line)
                if 'id' not in request:
                    continue
                method, params = request.get('method'), request.get('params', {})
                if method == 'initialize':
                    result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                              'serverInfo': {'name': 'looker-report-helper', 'version': '0.3.0'}}
                elif method == 'ping':
                    result = {}
                elif method in ('tools/list', 'tools/call'):
                    if bridge is None:
                        bridge = Bridge(args.endpoint)
                    if method == 'tools/list':
                        browser = bridge.call(method, params)
                        result = {'tools': [*TOOLS, *browser['tools']]}
                    elif params.get('name', '').startswith('looker_'):
                        result = execute(bridge, params['name'], params.get('arguments', {}))
                    else:
                        result = bridge.call(method, params)
                else:
                    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'error': {'code': -32601, 'message': 'Method not found'}}), flush=True)
                    continue
                response = {'jsonrpc': '2.0', 'id': request['id'], 'result': result}
            except Exception as exc:
                if isinstance(request, dict) and 'id' in request and request.get('method') == 'tools/call':
                    response = {'jsonrpc': '2.0', 'id': request['id'], 'result': {
                        'isError': True, 'content': [{'type': 'text', 'text': str(exc) + '\nInspect the report before retrying a mutation.'}]}}
                else:
                    response = {'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request, dict) else None,
                                'error': {'code': -32603, 'message': str(exc)}}
            print(json.dumps(response, ensure_ascii=False), flush=True)
    finally:
        if bridge:
            bridge.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
