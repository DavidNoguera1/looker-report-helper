"""Checkpointed chart workflows. The model supplies intent; this module sequences UI tools."""
import hashlib
import json
from pathlib import Path
import tempfile

TYPES = {'table':'simple-table', 'bar':'simple-barchart', 'scorecard':'kpi-metric',
         'pie':'simple-piechart', 'time_series':'simple-linechart', 'pivot':'pivot-table'}
PALETTES = {
    'ocean': {'background':'#f0fdfa','title':'#134e4a','text':'#134e4a','series':'#0d9488',
              'table_header':'#ccfbf1','table_header_text':'#134e4a','table_even':'#f0fdfa','table_odd':'#ffffff'},
    'light': {'background':'#ffffff','title':'#0f172a','text':'#334155','series':'#2563eb',
              'table_header':'#e2e8f0','table_header_text':'#0f172a','table_even':'#f8fafc','table_odd':'#ffffff'},
    'dark': {'background':'#0f172a','title':'#f8fafc','text':'#e2e8f0','series':'#38bdf8',
             'legend':'#e2e8f0','x_labels':'#e2e8f0','y_labels':'#e2e8f0','grid':'#475569',
             'table_header':'#1e293b','table_header_text':'#f8fafc','table_even':'#1e293b','table_odd':'#0f172a'},
}


class WorkflowError(RuntimeError):
    pass


def geometry_for(args, inventory):
    """Find a free rectangle in canvas pixels; never silently overlap or grow the page."""
    if all(k in args for k in ('x','y','width','height')):
        rectangle = {k: args[k] for k in ('x','y','width','height')}
        if rectangle['x']+rectangle['width']>inventory['canvas']['width'] or rectangle['y']+rectangle['height']>inventory['canvas']['height']:
            raise WorkflowError('OUTSIDE_CANVAS: choose a rectangle inside the current page.')
        return rectangle
    width, height = (220, 120) if args['type']=='scorecard' else (480, 260)
    for y in range(30, inventory['canvas']['height']-height+1, 20):
        for x in range(30, inventory['canvas']['width']-width+1, 20):
            if all(x+width+16<=c['x'] or c['x']+c['width']+16<=x or
                   y+height+16<=c['y'] or c['y']+c['height']+16<=y for c in inventory['components']):
                return {'x':x,'y':y,'width':width,'height':height}
    raise WorkflowError('NO_SPACE: specify a rectangle, edit an existing component, or add space through the UI.')


def build_chart(args, call, state_dir=None):
    """call(name, arguments) returns an action's structured result or raises on failure."""
    root = Path(state_dir) if state_dir else Path.home()/'.cache/looker-report-helper/runs'
    root.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256((args['report_id']+'\0'+args['request_id']).encode()).hexdigest()
    path = root/(key+'.json')
    fingerprint = hashlib.sha256(json.dumps(args,sort_keys=True).encode()).hexdigest()
    state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'fingerprint':fingerprint}
    if state['fingerprint'] != fingerprint:
        raise WorkflowError('REQUEST_ID_REUSED: parameters changed. Use a new request_id for a new design.')
    completed = []
    stage = 'inventory'
    last_arguments = {}
    applied_palette = {}

    def save():
        # Store IDs and checkpoints locally, never report values or credentials.
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=root,delete=False) as handle:
            json.dump(state,handle)
            temporary = Path(handle.name)
        temporary.replace(path)

    def step(name, **kwargs):
        nonlocal stage, last_arguments
        stage=name
        last_arguments=kwargs
        result=call('looker_'+name,{'report_id':args['report_id'],**kwargs})
        completed.append(name)
        return result

    try:
        inventory=step('inventory')
        if state.get('page_id') and state['page_id']!=inventory.get('page_id'):
            raise WorkflowError('WRONG_PAGE: resume on the original report page.')
        state['page_id']=inventory.get('page_id')
        component_id=state.get('component_id') or args.get('component_id')
        if not component_id and state.get('creation_pending'):
            # A timeout may hide a successful insert. Adopt only one new matching rectangle.
            candidates=[c for c in inventory['components'] if c['id'] not in state['before_ids']
                        and TYPES[args['type']] in c['type']
                        and all(abs(c[k]-state['rectangle'][k])<=2 for k in ('x','y','width','height'))]
            if len(candidates)!=1:
                raise WorkflowError('CREATION_UNCERTAIN: inspect inventory. This request will not insert again automatically.')
            component_id=candidates[0]['id']
        if component_id:
            matches=[c for c in inventory['components'] if c['id']==component_id]
            if len(matches)!=1 or TYPES[args['type']] not in matches[0]['type']:
                raise WorkflowError('COMPONENT_MISMATCH: ID is missing or chart type differs from the request.')
        else:
            rectangle=geometry_for(args,inventory)
            state.update(creation_pending=True,before_ids=[c['id'] for c in inventory['components']],rectangle=rectangle)
            save()  # Persist BEFORE insert, not after a potentially ambiguous timeout.
            created=step('create',type=args['type'],**rectangle)
            component_id=created['component']['id']
            state['component_id']=component_id
            save()
            if not created.get('geometry_verified'):
                raise WorkflowError('LAYOUT_UNVERIFIED: component exists; resume with its saved ID.')
        state.update(component_id=component_id,creation_pending=False)
        save()
        desired_rectangle={k:args[k] for k in ('x','y','width','height')} if all(k in args for k in ('x','y','width','height')) else state.get('rectangle')
        if desired_rectangle:
            step('layout',component_id=component_id,**desired_rectangle)
        step('set_title',component_id=component_id,title=args['title'])
        step('set_source',component_id=component_id,source=args['source'])
        slots=[('metric',args['metric'])]
        if args.get('dimension'):
            slots.insert(0,('pivot_row' if args['type']=='pivot' else 'dimension',args['dimension']))
        if args.get('column_dimension'):
            slots.insert(1,('pivot_column',args['column_dimension']))
        # Validate every requested name against the selected source before replacing slots.
        for slot,field in slots:
            found=step('fields',component_id=component_id,slot=slot,query=field,limit=100)
            if found['source']!=args['source']:
                raise WorkflowError('SOURCE_MISMATCH: field picker belongs to a different source.')
            if not any(f['name']==field for f in found['fields']):
                raise WorkflowError('FIELD_NOT_FOUND: requested '+slot+' name is absent from the selected source: '+field)
        for slot,field in slots:
            step('set_field',component_id=component_id,slot=slot,field=field)
        if args.get('sort_field'):
            step('set_sort',component_id=component_id,field=args['sort_field'],direction=args.get('sort_direction','ascending'))
        if args.get('palette'):
            available=step('inspect_style',component_id=component_id)
            for property,color in PALETTES[args['palette']].items():
                if property in available['colors'] or property=='series' and any(s['index']==0 for s in available['series']):
                    step('set_color',component_id=component_id,property=property,color=color)
                    applied_palette[property]=color
        final=step('inspect',component_id=component_id)
        if final.get('issues'):
            raise WorkflowError('CHART_ISSUE: '+', '.join(final['issues']))
        state['status']='complete';save()
        return {'status':'complete','component_id':component_id,'completed_steps':completed,
                'chart':final,'palette_applied':applied_palette,'saved_persistence_verified':False,'numerical_accuracy_verified':False,
                'next':'Reload and verify persistence, values and aggregation. Repeat the same request_id to reconcile without another insert.'}
    except Exception as exc:
        state['status']='partial';save()
        return {'status':'partial','component_id':state.get('component_id'),'failed_step':stage,
                'completed_steps':completed,'error':str(exc),'failed_arguments':last_arguments,'request_id':args['request_id'],
                'next':'Inspect the reported problem. Resume with identical arguments and request_id; do not invent another request_id to retry an uncertain creation.'}
