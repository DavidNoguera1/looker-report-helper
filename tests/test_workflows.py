"""Exercise recovery around real side-effect boundaries, using a simulated UI adapter."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'automation'))
from workflows import build_chart, WorkflowError, geometry_for

ARGS = dict(report_id='test-report', request_id='chart-1', type='bar', title='Annual totals',
            source='Example source', dimension='Year', metric='Total')


class UI:
    def __init__(self):
        self.inventory = dict(page_id='page-one', canvas=dict(width=1200, height=900), components=[])
        self.calls = []
        self.fail_after_insert = False
        self.missing_field = False

    def __call__(self, name, args):
        self.calls.append((name, args))
        if name == 'looker_inventory':
            return copy.deepcopy(self.inventory)
        if name == 'looker_create':
            component = dict(id='cd-new', type='simple-barchart', **{k:args[k] for k in ('x','y','width','height')})
            self.inventory['components'].append(component)
            if self.fail_after_insert:
                raise TimeoutError('Response lost after insert')
            return dict(component=component, geometry_verified=True)
        if name == 'looker_fields':
            return dict(source='Example source', fields=[] if self.missing_field else [dict(name=args['query'])])
        if name == 'looker_inspect_style':
            return dict(colors=dict(background='#fff', title='#000'), series=[])
        return dict(issues=[])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ui = UI()

    def run_chart(self, **changes):
        return build_chart({**ARGS, **changes}, self.ui, self.temp.name)

    def test_replay_reconciles_without_duplicate_and_limits_palette_to_available_controls(self):
        for _ in range(2):
            result = self.run_chart(palette='ocean')
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(set(result['palette_applied']), {'background', 'title'})
        self.assertEqual(sum(n=='looker_create' for n,a in self.ui.calls), 1)

    def test_recovers_component_after_lost_creation_response(self):
        self.ui.fail_after_insert = True
        first = self.run_chart()
        self.assertEqual(first['status'], 'partial')
        self.assertEqual(first['failed_step'], 'create')
        second = self.run_chart()
        self.assertEqual(second['status'], 'complete')
        self.assertEqual(second['component_id'], 'cd-new')
        self.assertEqual(sum(n=='looker_create' for n,a in self.ui.calls), 1)

    def test_uncertain_creation_never_blindly_inserts_again(self):
        self.ui.fail_after_insert = True
        self.run_chart()
        self.ui.inventory['components'].clear()
        result = self.run_chart()
        self.assertIn('CREATION_UNCERTAIN', result['error'])
        self.assertEqual(sum(n=='looker_create' for n,a in self.ui.calls), 1)

    def test_fields_are_preflighted_and_retry_keeps_component(self):
        self.ui.missing_field = True
        result = self.run_chart()
        self.assertEqual(result['component_id'], 'cd-new')
        self.assertIn('FIELD_NOT_FOUND', result['error'])
        self.assertFalse(any(n=='looker_set_field' for n,a in self.ui.calls))
        self.ui.missing_field = False
        self.assertEqual(self.run_chart()['status'], 'complete')
        self.assertEqual(sum(n=='looker_create' for n,a in self.ui.calls), 1)

    def test_changed_intent_requires_a_new_request_id(self):
        self.run_chart()
        before = len(self.ui.calls)
        with self.assertRaisesRegex(WorkflowError, 'REQUEST_ID_REUSED'):
            self.run_chart(title='Different request')
        self.assertEqual(len(self.ui.calls), before)

    def test_resume_on_wrong_page_stops_before_mutation(self):
        self.run_chart()
        self.ui.inventory['page_id'] = 'page-two'
        self.ui.calls.clear()
        result = self.run_chart()
        self.assertIn('WRONG_PAGE', result['error'])
        self.assertEqual([n for n,a in self.ui.calls], ['looker_inventory'])

    def test_auto_placement_avoids_occupied_space_and_rejects_full_canvas(self):
        rect = geometry_for(ARGS, self.ui.inventory)
        self.ui.inventory['components'] = [rect]
        second = geometry_for(ARGS, self.ui.inventory)
        self.assertGreaterEqual(second['x'], rect['x']+rect['width']+16)
        self.ui.inventory['components'] = [dict(x=0,y=0,width=1200,height=900)]
        with self.assertRaisesRegex(WorkflowError, 'NO_SPACE'):
            geometry_for(ARGS, self.ui.inventory)
        with self.assertRaisesRegex(WorkflowError, 'OUTSIDE_CANVAS'):
            geometry_for({**ARGS, 'x':1000,'y':30,'width':480,'height':260}, self.ui.inventory)


if __name__ == '__main__':
    unittest.main()
