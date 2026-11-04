"""Hourly delivery and nightly full-day analysis, without network or paid calls."""
import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import yaml

with patch.dict(os.environ, {'LITELLM_LOCAL_MODEL_COST_MAP': 'True'}):
    from trendradar.__main__ import NewsAnalyzer
    from trendradar.ai.analyzer import AIAnalyzer, AIAnalysisResult
    from trendradar.core.scheduler import Scheduler
    from trendradar.notification.ledger import PushLedger
    from trendradar.core.frequency import load_frequency_words


def groups(urls):
    return [{'word': 'Source', 'count': len(urls), 'titles': [
        {'title': url, 'url': url, 'source_name': 'Source'} for url in urls]}] if urls else []


class HourlyDigestTests(unittest.TestCase):
    def test_every_hour_and_only_22_analyzes_daily(self):
        config = yaml.safe_load(Path('config/config.yaml').read_text(encoding='utf-8'))
        timeline = yaml.safe_load(Path('config/timeline.yaml').read_text(encoding='utf-8'))
        for day in range(2, 9):
            for hour in range(24):
                now = datetime(2026, 11, day, hour, 5)
                schedule = Scheduler(config['schedule'], timeline, MagicMock(), lambda: now).resolve()
                self.assertTrue(schedule.collect)
                self.assertTrue(schedule.push)
                self.assertEqual(schedule.analyze, hour == 22)
                self.assertEqual(schedule.report_mode, 'daily' if hour == 22 else 'current')
                self.assertEqual(schedule.once_push, hour == 22)
        self.assertEqual(load_frequency_words(), ([], [], []))

    def test_no_duplicate_across_instances_or_midnight(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'push-state.json'
            ledger = PushLedger(path)
            selected, keys = ledger.select(groups(['https://example.com/old']))
            ledger.commit(keys)
            next_day = PushLedger(path)
            selected, keys = next_day.select(groups(['https://example.com/old', 'https://example.com/new']))
            self.assertEqual([x['url'] for x in selected[0]['titles']], ['https://example.com/new'])
            self.assertEqual(keys, {'https://example.com/new'})

    def test_baseline_unchanged_delivery_failure_and_summary_only(self):
        with TemporaryDirectory() as directory:
            analyzer = NewsAnalyzer.__new__(NewsAnalyzer)
            ctx = MagicMock()
            ctx.config = {'ENABLE_NOTIFICATION': True, 'NOTIFICATION_NEW_ONLY': True,
                          'STORAGE': {'LOCAL': {'DATA_DIR': directory}},
                          'AI_ANALYSIS': {'ENABLED': False}, 'SHOW_VERSION_UPDATE': False}
            ctx.platform_ids = ['test']
            ctx.prepare_report.side_effect = lambda stats, *args, **kwargs: {'stats': stats}
            dispatcher = ctx.create_notification_dispatcher.return_value
            dispatcher.dispatch_all.return_value = {'feishu': True}
            analyzer.ctx = ctx
            analyzer._has_notification_configured = lambda: True
            analyzer._has_valid_content = lambda stats, new: bool(stats)
            analyzer._run_ai_analysis = MagicMock(return_value=None)
            analyzer.frequency_file = None
            analyzer.proxy_url = None
            analyzer.report_mode = 'current'
            for name in ('_hotlist_total_count', '_rss_matched_count', '_rss_total_count', '_rss_source_total', '_rss_source_failed'):
                setattr(analyzer, name, 0)
            hourly = SimpleNamespace(analyze=False, push=True, once_push=False, period_key=None)
            call = lambda items: analyzer._send_notification_if_needed(groups(items), 'Current', 'current', schedule=hourly)
            self.assertFalse(call(['https://example.com/one']))
            self.assertFalse(call(['https://example.com/one']))
            dispatcher.dispatch_all.assert_not_called()
            dispatcher.dispatch_all.return_value = {'feishu': False}
            self.assertFalse(call(['https://example.com/one', 'https://example.com/two']))
            self.assertNotIn('https://example.com/two', PushLedger(Path(directory) / 'push-state.json').seen)
            dispatcher.dispatch_all.return_value = {'feishu': True}
            self.assertTrue(call(['https://example.com/one', 'https://example.com/two']))
            sent = dispatcher.dispatch_all.call_args.kwargs['report_data']['stats']
            self.assertEqual(sent[0]['titles'][0]['url'], 'https://example.com/two')
            nightly = SimpleNamespace(analyze=True, push=True, once_push=False, period_key=None)
            self.assertTrue(analyzer._send_notification_if_needed(groups(['old']), 'Daily', 'daily',
                            rss_items=groups(['rss-old']), ai_result=AIAnalysisResult(success=True), schedule=nightly))
            sent = dispatcher.dispatch_all.call_args.kwargs
            self.assertEqual(sent['report_data']['stats'], [])
            self.assertEqual(sent['rss_items'], [])
            self.assertIsNotNone(sent['ai_analysis'])

    def test_batched_ai_covers_all_articles_without_truncation(self):
        with patch('trendradar.ai.analyzer.AIClient') as client:
            client.return_value.api_key = 'test-only-key'
            client.return_value.validate_config.return_value = (True, '')
            client.return_value.chat.return_value = json.dumps({'core_trends': 'summary'})
            analyzer = AIAnalyzer({'MODEL': 'test'}, {'ANALYZE_ALL_NEWS': True,
                'MAX_NEWS_FOR_ANALYSIS': 2, 'INCLUDE_RSS': True}, datetime.now)
            hot = groups(['hot-1', 'hot-2', 'hot-3'])
            rss = groups(['rss-1', 'rss-2'])
            result = analyzer.analyze(hot, rss)
            calls = client.return_value.chat.call_args_list
            self.assertEqual(len(calls), 4)  # three disjoint batches plus synthesis
            prompts = '\n'.join(call.args[0][-1]['content'] for call in calls[:-1])
            for title in ['hot-1', 'hot-2', 'hot-3', 'rss-1', 'rss-2']:
                self.assertIn(title, prompts)
            self.assertTrue(result.success)
            self.assertEqual(result.analyzed_news, 5)
            self.assertEqual(result.hotlist_analyzed, 3)
            self.assertEqual(result.rss_analyzed, 2)
