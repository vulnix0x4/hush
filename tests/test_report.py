import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('report', ROOT / 'skills/hush/scripts/render_report.py')
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'demo/ledger.json').read_text())

    def test_verified_counts_and_coverage(self):
        rendered, markdown = REPORT.render(self.data)
        self.assertIn('3 verified setting changes', markdown)
        self.assertIn('4/5 account/channel rows inspected', markdown)
        self.assertIn('2 rows needing follow-up', markdown)
        self.assertIn('Partial coverage', rendered)
        self.assertIn('Synthetic demonstration', rendered)

    def test_unsaved_attempt_not_counted(self):
        self.data['changes'][0]['status'] = 'staged'
        self.data['coverage'][0]['status'] = 'partial'
        self.data['coverage'][0]['next_action'] = 'Retry Save and reopen.'
        rendered, markdown = REPORT.render(self.data)
        self.assertIn('2 verified setting changes', markdown)
        self.assertIn('Intended; not verified', rendered)

    def test_missing_verification_or_undo_rejected(self):
        for key in ['evidence', 'undo', 'before']:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data['changes'][0][key] = ''
                with self.assertRaises(ValueError):
                    REPORT.render(data)

    def test_complete_with_blockers_rejected(self):
        self.data['run_status'] = 'complete'
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_complete_valid(self):
        self.data['coverage'] = self.data['coverage'][:3]
        self.data['changes'] = self.data['changes'][:2]
        self.data['run_status'] = 'complete'
        self.data['scope_complete'] = True
        self.data['access_requests'] = []
        self.assertIn('Complete discovered coverage', REPORT.render(self.data)[0])

    def test_unchanged_setting_not_a_change(self):
        self.data['changes'][0]['after'] = self.data['changes'][0]['before']
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_duplicate_setting_not_double_counted(self):
        row = copy.deepcopy(self.data['changes'][0])
        row['id'] = 'different-id'
        self.data['changes'].append(row)
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_missing_reference_and_bad_rows(self):
        for row in [None, 'text', {'id': 'x'}]:
            with self.subTest(row=row):
                data = copy.deepcopy(self.data)
                data['coverage'].append(row)
                with self.assertRaises(ValueError):
                    REPORT.render(data)
        self.data['changes'][0]['coverage_id'] = 'missing'
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_contradictory_coverage(self):
        self.data['changes'][0]['status'] = 'failed'
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_escaping_and_unicode(self):
        self.data['title'] = '<script>alert("x")</script> Café'
        self.data['coverage'][0]['notes'] = 'a | b\n<script>x</script>'
        rendered, markdown = REPORT.render(self.data)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('Café', rendered)
        self.assertIn('a \\| b &lt;script&gt;', markdown)
        self.assertNotIn('<script>', markdown)
        self.assertNotIn('src=', rendered)
        self.assertNotIn('href=', rendered)

    def test_empty_pass_not_complete(self):
        self.data['coverage'] = []
        self.data['changes'] = []
        self.data['run_status'] = 'complete'
        with self.assertRaises(ValueError):
            REPORT.render(self.data)


    def finished_web_data(self):
        data = copy.deepcopy(self.data)
        data['coverage'] = data['coverage'][:3]
        data['changes'] = data['changes'][:2]
        data['run_status'] = 'complete'
        data['scope_complete'] = True
        data.pop('access_requests', None)
        return data

    def test_done_web_rows_cannot_hide_phone_discovery_gap(self):
        for scope in (None, False):
            data = self.finished_web_data()
            if scope is None:
                del data['scope_complete']
            else:
                data['scope_complete'] = scope
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                REPORT.render(data)

    def test_pending_and_declined_access_prevent_completion(self):
        for status in ('pending', 'declined'):
            data = self.finished_web_data()
            data['access_requests'] = [{'id':'phone', 'status':status,
                'action':'Unlock Mirroring', 'notes':'Phone inspection outstanding'}]
            with self.subTest(status=status), self.assertRaises(ValueError):
                REPORT.render(data)

    def test_access_resume_changes_report_state(self):
        self.data['access_requests'] = [{'id':'phone', 'status':'pending',
            'action':'Unlock Mirroring', 'notes':'Continue web work meanwhile'}]
        self.assertIn('Awaiting access', REPORT.render(self.data)[0])
        self.data['access_requests'][0]['status'] = 'satisfied'
        self.data['access_requests'][0]['notes'] = 'Fresh screen confirmed access'
        self.assertNotIn('Awaiting access', REPORT.render(self.data)[0])
        self.assertIn('Partial coverage', REPORT.render(self.data)[0])

    def test_satisfied_access_allows_completed_scope(self):
        data = self.finished_web_data()
        data['access_requests'] = [{'id':'phone', 'status':'satisfied',
            'action':'Unlock Mirroring', 'notes':'Inspected after unlock'}]
        self.assertIn('Complete discovered coverage', REPORT.render(data)[0])

    def test_live_and_automated_evidence_kept_separate(self):
        self.data['test_results'] = [
            {'name':'Renderer', 'method':'automated', 'status':'passed', 'evidence':'Suite passed'},
            {'name':'Phone', 'method':'live', 'status':'blocked', 'evidence':'Needs unlock'},
            {'name':'Save', 'method':'live', 'status':'not_exercised', 'evidence':'No changes needed'},
            {'name':'Undo', 'method':'manual_review', 'status':'failed', 'evidence':'Original value unknown'}]
        rendered, markdown = REPORT.render(self.data)
        for value in ('automated, passed', 'live, blocked', 'live, not_exercised', 'manual_review, failed'):
            self.assertIn(value, rendered)
            self.assertIn(value.replace('_', r'\_'), markdown)

    def test_malformed_access_and_test_evidence_rejected(self):
        for key, value in (('access_requests', {}), ('test_results', [None]),
                           ('scope_complete', 'true'),
                           ('test_results', [{'name':'x','method':'pretend','status':'passed','evidence':'x'}])):
            data = copy.deepcopy(self.data)
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                REPORT.render(data)

    def test_duplicate_access_request_rejected(self):
        row = {'id':'phone', 'status':'pending', 'action':'Unlock', 'notes':'Needed'}
        self.data['access_requests'] = [row, row]
        with self.assertRaises(ValueError):
            REPORT.render(self.data)

    def test_new_evidence_fields_are_escaped(self):
        self.data['access_requests'] = [{'id':'phone', 'status':'pending',
            'action':'<img src=x onerror=alert(1)>', 'notes':'a | b'}]
        self.data['test_results'] = [{'name':'<script>x</script>', 'method':'live',
            'status':'blocked', 'evidence':'<iframe src=x>'}]
        rendered, markdown = REPORT.render(self.data)
        self.assertNotIn('<img ', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('<iframe ', rendered)
        self.assertIn('a \| b', markdown)

    def test_cli_rejects_input_output_collision_without_data_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            content = json.dumps(self.data)
            source.write_text(content)
            result = subprocess.run([sys.executable, str(SPEC.origin), str(source), '--out', tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_text(), content)
            self.assertFalse((Path(tmp) / 'report.html').exists())

    def test_cli_writes_both_outputs_from_real_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'ledger.json'
            source.write_text(json.dumps(self.data))
            output = Path(tmp) / 'report'
            result = subprocess.run([sys.executable, str(SPEC.origin), str(source), '--out', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Hush', (output / 'report.html').read_text())
            self.assertIn('3 verified setting changes', (output / 'report.md').read_text())


if __name__ == '__main__':
    unittest.main()
