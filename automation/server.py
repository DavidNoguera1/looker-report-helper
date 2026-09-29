"""Serve deterministic Looker UI actions plus the official Playwright tools over MCP."""
import argparse
import json
import re
import sys
from bridge import Bridge, ROOT
from workflows import build_chart, PALETTES

STRING = {'type': 'string', 'minLength': 1, 'maxLength': 200}
REPORT = {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{1,100}$'}
COMPONENT = {'type': 'string', 'pattern': '^cd-[A-Za-z0-9_-]{1,100}$'}
SLOTS = ['metric', 'dimension', 'pivot_row', 'pivot_column']
COLOR_PROPERTIES = ['background', 'title', 'text', 'border', 'legend', 'plot_background',
                    'table_header', 'table_header_text', 'table_even', 'table_odd',
                    'axis', 'x_labels', 'y_labels', 'grid', 'series']
HEX_COLOR = {'type': 'string', 'pattern': '^#[0-9A-Fa-f]{6}$'}
GEOMETRY = {k: {'type': 'integer', 'minimum': 0 if k in ('x', 'y') else 20, 'maximum': 4000}
            for k in ('x', 'y', 'width', 'height')}


def tool(name, description, properties, required=None, readonly=False):
    properties = {'report_id': REPORT, **properties}
    return {'name': 'looker_' + name, 'description': description,
            'inputSchema': {'type': 'object', 'properties': properties,
                            'required': ['report_id', *(required if required is not None else [key for key in properties if key != 'report_id'])],
                            'additionalProperties': False},
            'annotations': {'readOnlyHint': readonly, 'destructiveHint': False,
                            'idempotentHint': name in ('inventory', 'layout', 'set_field', 'set_title',
                                                      'set_sort', 'set_source', 'set_color')}}


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
    tool('sources', 'List exact source names available to this chart, distinguishing added and available sources. Does not change the source or verify access.',
         {'component_id': COMPONENT}),
    tool('set_source', 'Switch this chart to an existing source by exact name from looker_sources. Does not edit the shared source connection. Inspect/remap fields afterward; selection does not prove data access.',
         {'component_id': COMPONENT, 'source': STRING}),
    tool('fields', 'Discover field names and type icons for the current chart source. Search with query to narrow a large schema. Returns has_more for virtualized lists; does not change a field.',
         {'component_id': COMPONENT, 'slot': {'type':'string', 'enum':SLOTS},
          'query': {'type':'string', 'minLength':0, 'maxLength':200},
          'limit': {'type':'integer', 'minimum':1, 'maximum':200}}, ['component_id']),
    tool('inspect_style', 'List available color properties and enabled series colors for this chart. Use these property names with looker_set_color.',
         {'component_id': COMPONENT}),
    tool('set_color', 'Set one available chart color through the actual color picker. Use a six-digit #RRGGBB value; series_index defaults to 0. Verify colors after reloading for persistence.',
         {'component_id': COMPONENT, 'property': {'type':'string','enum':COLOR_PROPERTIES},
          'color': HEX_COLOR, 'series_index': {'type':'integer','minimum':0,'maximum':19}},
         ['component_id','property','color']),
    tool('build_chart', 'Create or update a complete chart: place it, set source, verify field names, set fields/title/sort and apply a palette. Start with sources/fields discovery. Use a stable request_id; repeat IDENTICAL arguments to resume a partial result without inserting again. For edits supply component_id. Geometry is optional (auto-place new charts).',
         {'request_id': {'type':'string','pattern':'^[A-Za-z0-9_-]{1,80}$'},
          'component_id': COMPONENT, 'type': {'type':'string','enum':['table','scorecard','bar','pie','time_series','pivot']},
          'title':STRING,'source':STRING,'metric':STRING,'dimension':STRING,'column_dimension':STRING,
          **GEOMETRY,'sort_field':STRING,'sort_direction':{'type':'string','enum':['ascending','descending']},
          'palette':{'type':'string','enum':list(PALETTES)}}, ['request_id','type','title','source','metric']),
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
        elif not isinstance(value, str) or len(value) < field.get('minLength', 1) or len(value) > field.get('maxLength', 200):
            raise ValueError('Invalid string: ' + key)
        if 'enum' in field and value not in field['enum']:
            raise ValueError('Invalid choice: ' + key)
        if 'pattern' in field and re.fullmatch(field['pattern'], value) is None:
            raise ValueError('Invalid identifier: ' + key)
    if name == 'looker_build_chart':
        geometry=set(arguments)&set(GEOMETRY)
        if geometry and geometry!=set(GEOMETRY):
            raise ValueError('Provide all of x, y, width and height, or omit all four.')
        if arguments['type']!='scorecard' and not arguments.get('dimension'):
            raise ValueError('This chart type requires dimension (use an exact source field name).')
        if arguments['type']=='scorecard' and arguments.get('dimension'):
            raise ValueError('A scorecard workflow accepts one metric, not a dimension.')
        if (arguments['type']=='pivot') != bool(arguments.get('column_dimension')):
            raise ValueError('column_dimension is required only for a pivot chart.')
        if arguments.get('sort_field') and arguments['type'] not in ('table','bar','pie'):
            raise ValueError('Primary sorting is currently supported for table, bar and pie workflows.')
        if arguments.get('sort_direction') and not arguments.get('sort_field'):
            raise ValueError('sort_direction requires sort_field.')
    return {'action': name.removeprefix('looker_'), **arguments}


def execute(bridge, name, arguments):
    args = validate(name, arguments)
    if name == 'looker_build_chart':
        def call(action, parameters):
            response=execute(bridge, action, parameters)
            if response.get('isError'):
                raise RuntimeError('\n'.join(c.get('text','') for c in response.get('content',[])))
            if 'structuredContent' not in response:
                raise RuntimeError('UNEXPECTED_RESULT: browser did not return structured evidence.')
            return response['structuredContent']
        data=build_chart(arguments,call)
        return {'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}],
                'structuredContent':data,'isError':data['status']=='partial'}
    source = (ROOT / 'automation/looker.js').read_text(encoding='utf-8')
    code = 'async (page) => {\n' + source + '\nreturn await lookerAction(page, ' + json.dumps(args, ensure_ascii=True) + ');\n}'
    result = bridge.call('tools/call', {'name': 'browser_run_code_unsafe', 'arguments': {'code': code}})
    # Keep deterministic tools concise. The underlying tool echoes its entire program.
    for item in result.get('content', []):
        if item.get('type') == 'text':
            item['text'] = item['text'].split('\n### Ran Playwright code')[0]
            if not result.get('isError') and item['text'].startswith('### Result\n'):
                try:
                    data=json.loads(item['text'][len('### Result\n'):].strip())
                    if isinstance(data,dict):
                        result['structuredContent']=data
                        item['text']=json.dumps(data,ensure_ascii=False)
                except ValueError:
                    pass
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', help='Development only: existing local Playwright MCP HTTP endpoint')
    parser.add_argument('--call', choices=[t['name'] for t in TOOLS], help='Run one action with JSON arguments from stdin')
    parser.add_argument('--compact', action='store_true', help='Expose Looker tools and only basic browser navigation/inspection tools')
    args = parser.parse_args()
    if args.endpoint and not re.fullmatch(r'http://(?:localhost|127\.0\.0\.1):\d+/mcp', args.endpoint):
        parser.error('Only loopback HTTP endpoints are supported')
    sys.stdin.reconfigure(encoding='utf-8')
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
                              'serverInfo': {'name': 'looker-report-helper', 'version': '0.4.0'}}
                elif method == 'ping':
                    result = {}
                elif method in ('tools/list', 'tools/call'):
                    if bridge is None:
                        bridge = Bridge(args.endpoint)
                    if method == 'tools/list':
                        browser = bridge.call(method, params)
                        basic={'browser_tabs','browser_navigate','browser_snapshot','browser_take_screenshot'}
                        result = {'tools': [*TOOLS, *[t for t in browser['tools'] if not args.compact or t['name'] in basic]]}
                    elif params.get('name', '').startswith('looker_'):
                        result = execute(bridge, params['name'], params.get('arguments', {}))
                    else:
                        if args.compact and params.get('name') not in {'browser_tabs','browser_navigate','browser_snapshot','browser_take_screenshot'}:
                            raise ValueError('Tool is not exposed in compact mode. Restart without --compact for advanced browser operations.')
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
