"""Source-card layout preserves all RSS entries and the legacy keyword layout."""
import unittest
from unittest.mock import patch
import os

with patch.dict(os.environ, {'LITELLM_LOCAL_MODEL_COST_MAP': 'True'}):
    from trendradar.report.html import render_html_content


class DashboardTest(unittest.TestCase):
    def test_source_layout_and_new_section(self):
        report = {'stats': [], 'failed_ids': [], 'new_titles': [], 'total_new_count': 0}
        rss = [{'word': 'Test source', 'count': 25, 'titles': [
            {'title': f'Article {i}', 'url': f'https://example.com/{i}', 'feed_name': 'Test source'}
            for i in range(25)
        ]}]
        html = render_html_content(report, 0, rss_items=rss, rss_new_items=rss,
                                   display_mode='platform', show_new_section=False)
        self.assertIn('id="source-dashboard-style"', html)
        self.assertIn('id="source-dashboard-script"', html)
        self.assertEqual(html.count('class="rss-item"'), 25)
        self.assertNotIn('RSS 新增更新', html)
        self.assertIn('https://example.com/24', html)
        legacy = render_html_content(report, 0, rss_items=rss, rss_new_items=rss)
        self.assertNotIn('id="source-dashboard-style"', legacy)
        self.assertEqual(legacy.count('class="rss-item"'), 50)


if __name__ == '__main__':
    unittest.main()
