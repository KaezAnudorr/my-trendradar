"""Check only the unresolved native-feed choices and IT article links."""
import json
import re
from pathlib import Path
import requests
from trendradar.crawler.rss.parser import RSSParser

checks = [
    ('hacker-news-30', 'https://hnrss.org/frontpage?count=30', True),
    ('ithome-native', 'https://www.ithome.com/rss/', True),
    ('ithome-dailyhot-article', 'https://www.ithome.com/0/102/0930.htm', False),
    ('ithome-existing-article', 'https://www.ithome.com/1/021/648.htm', False),
]
results = []
for name, url, is_feed in checks:
    result = {'name': name, 'url': url}
    try:
        response = requests.get(url, timeout=20, headers={'User-Agent': 'TrendRadar/2.0 RSS Reader'})
        result['http_status'] = response.status_code
        response.raise_for_status()
        response.encoding = 'utf-8'
        if is_feed:
            items = RSSParser().parse(response.text, url)
            result.update(items=len(items), unique=len({i.url for i in items}),
                          summaries=sum(bool(i.summary) for i in items),
                          published=sum(bool(i.published_at) for i in items),
                          samples=[{'title': i.title, 'url': i.url} for i in items[:3]])
        else:
            title = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.S | re.I)
            result['page_title'] = title.group(1).strip() if title else ''
    except (requests.RequestException, ValueError) as error:
        result['error'] = str(error)
    results.append(result)
    print(json.dumps(result, ensure_ascii=False))
Path('dailyhot-followup.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
