"""DailyHot preserves true article metadata instead of inventing publication dates."""
import json
import unittest
import runpy
from contextlib import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, Mock
import requests
import yaml
from tools.dailyhot_feeds import make_feed
from trendradar.crawler.rss.parser import RSSParser


class DailyHotFeedTest(unittest.TestCase):
    def test_metadata_and_parser_roundtrip(self):
        raw = {'code': 200, 'updateTime': '2026-11-03T09:00:00Z', 'data': [
            {'title': 'Article', 'url': 'https://example.com/one', 'timestamp': 1700000000000,
             'desc': 'Original summary', 'author': 'Author'},
            {'title': 'Without publication date', 'url': 'https://example.com/two', 'timestamp': 0},
            {'title': 'Broken link', 'url': '获取失败'},
        ]}
        feed = make_feed(raw, 'Source · 热榜快照')
        items = RSSParser().parse(json.dumps(feed))
        self.assertEqual(len(items), 2)
        self.assertTrue(items[0].published_at.startswith('2023-11-14'))
        self.assertEqual(items[0].summary, 'Original summary')
        self.assertEqual(items[0].author, 'Author')
        self.assertIsNone(items[1].published_at)
        self.assertNotIn('date_published', feed['items'][1])

    def test_failed_or_empty_source_is_not_enabled(self):
        for raw in [{'code': 500, 'data': []}, {'code': 200, 'data': []}]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                make_feed(raw, 'Source')

    def test_runner_overlay_preserves_settings_and_skips_failed_source(self):
        script = Path(__file__).resolve().parents[1] / 'tools/dailyhot_feeds.py'
        original = {'rss': {'keyword_filter': False, 'feeds': [
            {'id': 'existing', 'name': 'Existing', 'url': 'https://example.com/rss', 'max_age_days': 3}
        ]}, 'ai_analysis': {'enabled': False}, 'notification': {'enabled': False}}
        response = Mock()
        response.json.return_value = {'code': 200, 'data': [{'title': 'New', 'url': 'https://example.com/new'}]}
        with TemporaryDirectory() as directory, chdir(directory):
            Path('config').mkdir()
            Path('integrations/dailyhot').mkdir(parents=True)
            Path('config/config.yaml').write_text(yaml.safe_dump(original), encoding='utf-8')
            Path('integrations/dailyhot/feeds.yaml').write_text(yaml.safe_dump({'feeds': [
                {'id': 'new', 'route': 'new', 'name': 'New'},
                {'id': 'broken', 'route': 'broken', 'name': 'Broken'},
            ]}), encoding='utf-8')
            with patch('requests.get', side_effect=[response, requests.HTTPError('503')]):
                runpy.run_path(str(script), run_name='__main__')
            config = yaml.safe_load(Path('config/config.yaml').read_text(encoding='utf-8'))
            self.assertEqual(config['rss']['feeds'][0], original['rss']['feeds'][0])
            self.assertEqual([feed['id'] for feed in config['rss']['feeds']], ['existing', 'new'])
            self.assertEqual(config['rss']['feeds'][1]['max_age_days'], 0)
            self.assertEqual(config['ai_analysis'], original['ai_analysis'])
            self.assertEqual(config['notification'], original['notification'])
            exported = Path('output/dailyhot/new.json').read_text(encoding='utf-8')
            self.assertEqual(RSSParser().parse(exported)[0].title, 'New')
