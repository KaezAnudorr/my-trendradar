"""Source grouping covers RSS alongside hotlists without changing keyword mode."""

import copy
import os
import unittest
from unittest.mock import MagicMock, patch

with patch.dict(os.environ, {"LITELLM_LOCAL_MODEL_COST_MAP": "True"}):
    from trendradar.__main__ import NewsAnalyzer
    from trendradar.notification.renderer import render_feishu_content


class SourceGroupingTests(unittest.TestCase):
    def test_pipeline_groups_rss_for_both_filter_strategies(self):
        rss = [
            {"word": "AI", "count": 2, "titles": [
                {"title": "First", "source_name": "Huxiu", "url": "https://example.com/1",
                 "ranks": [1], "count": 1, "is_new": True, "time_display": "12:00"},
                {"title": "Second", "source_name": "Wallstreet", "url": "https://example.com/2",
                 "ranks": [2], "count": 1, "is_new": False, "time_display": "11:00"},
            ]},
            {"word": "Tools", "count": 1, "titles": [
                {"title": "Third", "source_name": "Huxiu", "url": "https://example.com/3",
                 "ranks": [3], "count": 1, "is_new": True, "time_display": "10:00"},
            ]},
        ]
        original = copy.deepcopy(rss)
        for strategy in ("keyword", "ai"):
            for mode in ("platform", "keyword"):
                with self.subTest(strategy=strategy, mode=mode):
                    analyzer = NewsAnalyzer.__new__(NewsAnalyzer)
                    analyzer.filter_method = strategy
                    analyzer.interests_file = None
                    ctx = MagicMock()
                    ctx.display_mode = mode
                    ctx.rank_threshold = 5
                    ctx.weight_config = {
                        "RANK_WEIGHT": 0.6, "FREQUENCY_WEIGHT": 0.3, "HOTNESS_WEIGHT": 0.1,
                    }
                    ctx.config = {"STORAGE": {"FORMATS": {"HTML": False}}}
                    ctx.count_frequency.return_value = ([], 0)
                    ctx.convert_ai_filter_to_report_data.return_value = ([], rss, rss[:1])
                    analyzer.ctx = ctx
                    result = analyzer._run_analysis_pipeline(
                        {}, "current", {}, {}, [], [], {},
                        rss_items=rss, rss_new_items=rss[:1],
                    )
                    main, new = result[3], result[5]
                    expected = ["Huxiu", "Wallstreet"] if mode == "platform" else ["AI", "Tools"]
                    self.assertEqual([group["word"] for group in main], expected)
                    self.assertEqual([group["word"] for group in new],
                                     ["Huxiu", "Wallstreet"] if mode == "platform" else ["AI"])
                    self.assertEqual(analyzer._rss_matched_count, 3)
                    if mode == "platform":
                        self.assertEqual([item["title"] for item in main[0]["titles"]], ["First", "Third"])
                        self.assertEqual(main[0]["titles"][0]["url"], "https://example.com/1")
                        self.assertTrue(main[0]["titles"][0]["is_new"])
                        rendered = render_feishu_content(
                            {"stats": [], "new_titles": [], "failed_ids": []}, rss_items=main,
                        )
                        self.assertIn("Huxiu", rendered)
                        self.assertIn("Wallstreet", rendered)
                    else:
                        self.assertIs(main, rss)
        self.assertEqual(rss, original)


if __name__ == "__main__":
    unittest.main()
