"""Probe candidate DailyHot RSS routes without changing subscriptions."""
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROUTES = ['guokr', 'ifanr', 'geekpark', '51cto', 'csdn', 'hellogithub',
          'linuxdo', 'yystv', 'gameres', 'producthunt', 'weread', 'smzdm',
          'github', 'hackernews', 'huxiu', '36kr']


def probe(route):
    url = f'https://api-hot.imsyy.top/{route}?rss=true'
    result = {'route': route, 'url': url, 'usable': False}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'TrendRadar-source-check/1.0'})
        with urllib.request.urlopen(request, timeout=25) as response:
            result['http_status'] = response.status
            root = ET.fromstring(response.read())
        items = root.findall('./channel/item')
        valid = [item for item in items if item.findtext('title') and (item.findtext('link') or '').startswith(('https://', 'http://'))]
        result.update(items=len(items), valid_items=len(valid), usable=bool(valid) and len(valid) == len(items))
        if valid:
            result['sample_title'] = valid[0].findtext('title')
    except (urllib.error.URLError, TimeoutError, ET.ParseError) as error:
        result['error'] = str(error)
    return result


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(probe, ROUTES))
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'results': results}
    Path('dailyhot-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for result in results:
        print(json.dumps(result, ensure_ascii=False))
    print(f'Usable RSS routes: {sum(r["usable"] for r in results)}/{len(results)}')
