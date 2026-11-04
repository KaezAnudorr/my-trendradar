"""Persist delivered article identities independently of daily crawl databases."""
import json
from pathlib import Path


class PushLedger:
    def __init__(self, path):
        self.path = Path(path)
        self.exists = self.path.exists()
        self.seen = set(json.loads(self.path.read_text(encoding='utf-8'))) if self.exists else set()

    def select(self, groups):
        selected = []
        keys = set()
        for group in groups or []:
            titles = []
            for item in group['titles']:
                key = item.get('url') or f'{item.get("source_name", group["word"])}:{item["title"]}'
                if key not in self.seen and key not in keys:
                    keys.add(key)
                    titles.append(item)
            if titles:
                selected.append({**group, 'titles': titles, 'count': len(titles)})
        return selected, keys

    def commit(self, keys):
        self.seen.update(keys)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(sorted(self.seen), ensure_ascii=False), encoding='utf-8')
