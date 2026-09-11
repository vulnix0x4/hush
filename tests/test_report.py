import copy
import importlib.util
import json
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


if __name__ == '__main__':
    unittest.main()
