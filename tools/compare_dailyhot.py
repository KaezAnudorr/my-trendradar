"""Compare overlapping feeds from one runner, retaining article-level evidence."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
import yaml
from trendradar.crawler.rss.parser import RSSParser
from dailyhot_feeds import make_feed

PAIRS = [('sspai', 'sspai'), ('ithome', 'ithome'), ('36kr', '36kr'),
         ('huxiu-tech', 'huxiu'), ('v2ex-hot', 'v2ex'), ('zhihu-daily', 'zhihu-daily'),
         ('github-trending', 'github'), ('hacker-news', 'hackernews'), ('juejin-ai', 'juejin')]


def normalize(url):
    parts = urlsplit(url)
    return urlunsplit(('', parts.netloc.removeprefix('www.'), parts.path.rstrip('/'), parts.query, ''))


if __name__ == '__main__':
    feeds = {feed['id']: feed for feed in yaml.safe_load(Path('config/config.yaml').read_text(encoding='utf-8'))['rss']['feeds']}
    parser = RSSParser()
    results = []
    for current_id, route in PAIRS:
        pair = {'id': current_id, 'name': feeds[current_id]['name'], 'route': route}
        for side, url in [('current', feeds[current_id]['url']), ('dailyhot', f'http://127.0.0.1:6688/{route}')]:
            try:
                response = requests.get(url, timeout=25, headers={'User-Agent': 'TrendRadar/2.0 RSS Reader'})
                response.raise_for_status()
                response.encoding = 'utf-8'
                body = response.text
                raw_count = None
                if side == 'dailyhot':
                    raw = response.json()
                    raw_count = len(raw.get('data', []))
                    body = json.dumps(make_feed(raw, pair['name']))
                items = parser.parse(body, url)
                articles = [{'title': item.title, 'url': item.url, 'published_at': item.published_at,
                             'summary': item.summary, 'author': item.author} for item in items]
                pair[side] = {'items': len(items), 'returned': raw_count,
                              'valid_links': sum(item.url.startswith(('https://', 'http://')) for item in items),
                              'published': sum(bool(item.published_at) for item in items),
                              'summaries': sum(bool(item.summary) for item in items), 'articles': articles}
            except (requests.RequestException, ValueError) as error:
                pair[side] = {'error': str(error)}
        if 'articles' in pair['current'] and 'articles' in pair['dailyhot']:
            a = {normalize(item['url']) for item in pair['current']['articles']}
            b = {normalize(item['url']) for item in pair['dailyhot']['articles']}
            pair.update(overlap=len(a & b), current_only=len(a - b), dailyhot_only=len(b - a))
        results.append(pair)
        print(json.dumps({key: ({k: v for k, v in value.items() if k != 'articles'} if isinstance(value, dict) else value) for key, value in pair.items()}, ensure_ascii=False))
        time.sleep(10)  # Respect the existing RSSHub request interval.
    Path('dailyhot-comparison.json').write_text(json.dumps({'checked_at': datetime.now(timezone.utc).isoformat(), 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
