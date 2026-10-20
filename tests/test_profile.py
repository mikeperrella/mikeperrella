"""Offline regression checks. Run: python -m unittest discover -s tests -v"""
import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_fetch_module():
    spec = importlib.util.spec_from_file_location('fetch_contributions', ROOT / 'scripts' / 'fetch_contributions.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestProfile(unittest.TestCase):
    def test_json_snapshot_is_consistent(self):
        data = json.loads((ROOT / 'data' / 'contributions.json').read_text(encoding='utf-8'))
        self.assertEqual(data['username'], 'mikeperrella')
        self.assertEqual(data['total_contributions'], sum(d['count'] for d in data['days']))
        self.assertEqual(len({d['date'] for d in data['days']}), len(data['days']))
        self.assertTrue(all(0 <= d['level'] <= 4 for d in data['days']))

    def test_svg_files_are_well_formed(self):
        for name in ('mike-ascii.svg', 'stats.svg', 'contrib-heatmap.svg'):
            with self.subTest(name=name):
                root = ET.parse(ROOT / name).getroot()
                self.assertTrue(root.tag.endswith('svg'))

    def test_scraper_understands_comma_counts_and_zeros(self):
        mod = load_fetch_module()
        fixture = '''<table><tbody>
          <tr><td class="ContributionCalendar-day" id="d1" data-date="2026-10-19" data-level="4"></td>
              <td class="ContributionCalendar-day" id="d2" data-date="2026-10-20" data-level="0"></td></tr>
          </tbody></table>
          <tool-tip for="d1">1,234 contributions on October 19th.</tool-tip>
          <tool-tip for="d2">No contributions on October 20th.</tool-tip>'''
        class Response:
            text = fixture
            def raise_for_status(self): pass
        with patch.object(mod.requests, 'get', return_value=Response()):
            days = mod.fetch_days()
        self.assertEqual([d['count'] for d in days], [1234, 0])

    def test_readme_does_not_publish_contact_info(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertNotIn('mikerperrella@gmail.com', text)
        self.assertNotIn('732.810', text)
        self.assertIn('Private repository', text)

if __name__ == '__main__':
    unittest.main()
