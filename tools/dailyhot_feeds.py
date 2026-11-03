"""Export DailyHot JSON as JSON Feed, preserving actual item timestamps."""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml


def make_feed(data, title):
    # Validate external data here, before handing it to the existing RSS pipeline.
    if data.get('code') != 200 or not isinstance(data.get('data'), list):
        raise ValueError('DailyHot did not return a successful list')
    items = []
    seen = set()
    for raw in data['data']:
        url = raw.get('url', '')
        if not raw.get('title') or not url.startswith(('https://', 'http://')):
            continue
        if url in seen:
            continue
        seen.add(url)
        item = {'id': url, 'url': url, 'title': raw['title'], 'content_text': raw.get('desc') or ''}
        timestamp = raw.get('timestamp')
        if isinstance(timestamp, (int, float)) and timestamp > 0:
            item['date_published'] = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat()
        if raw.get('author'):
            item['authors'] = [{'name': raw['author']}]
        items.append(item)
    if not items:
        raise ValueError('DailyHot returned no usable articles')
    return {'version': 'https://jsonfeed.org/version/1.1', 'title': title, 'items': items}


if __name__ == '__main__':
    from trendradar.crawler.rss.parser import RSSParser

    specs = yaml.safe_load(Path('integrations/dailyhot/feeds.yaml').read_text(encoding='utf-8'))['feeds']
    path = Path('config/config.yaml')
    config = yaml.safe_load(path.read_text(encoding='utf-8'))
    output = Path('output/dailyhot')
    output.mkdir(parents=True, exist_ok=True)
    results = []
    additions = []
    for spec in specs:
        result = {'id': spec['id'], 'name': spec['name'], 'route': spec['route']}
        try:
            response = requests.get(f'http://127.0.0.1:6688/{spec["route"]}', timeout=25)
            response.raise_for_status()
            raw = response.json()
            feed = make_feed(raw, spec['name'])
            encoded = json.dumps(feed, ensure_ascii=False)
            parsed = RSSParser().parse(encoded)
            if len(parsed) != len(feed['items']):
                raise ValueError('TrendRadar parser dropped exported articles')
            (output / f'{spec["id"]}.json').write_text(encoded, encoding='utf-8')
            additions.append({'id': spec['id'], 'name': spec['name'],
                              'url': f'http://127.0.0.1:6689/{spec["id"]}.json', 'max_age_days': 0})
            result.update(status='enabled', returned=len(raw['data']), articles=len(parsed),
                          published=sum(bool(item.published_at) for item in parsed))
        except (requests.RequestException, ValueError) as error:
            result.update(status='failed', error=str(error))
            print(f'::warning title=DailyHot source unavailable::{spec["name"]}: {error}')
        results.append(result)
        print(json.dumps(result, ensure_ascii=False))
    (output / 'integration-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    config['rss']['feeds'].extend(additions)
    path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'DailyHot enabled {len(additions)}/{len(specs)} sources; existing sources preserved')
