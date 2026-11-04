"""Validate the four requested DailyHot APIs and prepare same-list alternatives."""
import json
from pathlib import Path
import requests
from trendradar.crawler.fetcher import DataFetcher

checks, platforms = [], {}
for route, domain in [('bilibili', 'bilibili.com'), ('weibo', 'weibo.com'),
                      ('douyin', 'douyin.com'), ('zhihu', 'zhihu.com')]:
    check = {'api': route, 'available': False}
    try:
        response = requests.get(f'http://127.0.0.1:6688/{route}', timeout=25)
        response.raise_for_status()
        data = response.json()
        if data.get('code') != 200 or not data.get('data'):
            raise ValueError('API returned no successful list')
        items = [item for item in data['data'] if item.get('title') and item.get('url', '').startswith('https://')]
        check.update(available=bool(items), articles=len(items), kind=data.get('type'), sample=items[0]['title'] if items else '')
        # Bilibili ranks videos, unlike the existing search-term hotlist: do not replace it.
        if route != 'bilibili':
            error = DataFetcher._check_domain_safety(items, domain)
            if error:
                raise ValueError(error)
            platforms[route] = {item['title']: {'ranks': [index], 'url': item['url'],
                                             'mobileUrl': item.get('mobileUrl', '')}
                                for index, item in enumerate(items, 1)}
    except (requests.RequestException, ValueError) as error:
        check.update(available=False, error=str(error))
    checks.append(check)
    print(json.dumps(check, ensure_ascii=False))
Path('output/dailyhot/four-apis.json').write_text(json.dumps({'checks': checks, 'platforms': platforms}, ensure_ascii=False), encoding='utf-8')
