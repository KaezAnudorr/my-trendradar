"""Local-only reader: sync the generated public-news snapshot and reload on change."""
import argparse
import json
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    directory = Path(args.directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    report = directory / 'current.html'
    state = {'revision': report.stat().st_mtime_ns if report.exists() else 0, 'error': None}

    def sync():
        etag = None
        while True:
            headers = {'User-Agent': 'TrendRadar-local-preview'}
            if etag:
                headers['If-None-Match'] = etag
            try:
                request = Request('https://raw.githubusercontent.com/KaezAnudorr/my-trendradar/generated-preview/current.html', headers=headers)
                with urlopen(request, timeout=20) as response:
                    data = response.read()
                    etag = response.headers.get('ETag')
                if b'<html' not in data.lower():
                    raise ValueError('Snapshot is not an HTML report')
                if not report.exists() or report.read_bytes() != data:
                    report.write_bytes(data)
                    state['revision'] = report.stat().st_mtime_ns
                state['error'] = None
            except HTTPError as error:
                state['error'] = None if error.code == 304 else str(error)
            except (URLError, TimeoutError, ValueError) as error:
                state['error'] = str(error)
            time.sleep(60)

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?')[0] == '/preview-status.json':
                data = json.dumps(state).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif self.path.split('?')[0] in ('/', '/current.html') and report.exists():
                script = '''<script>
const previewRevision = REVISION;
setInterval(async () => {
  const state = await (await fetch('/preview-status.json', {cache:'no-store'})).json();
  if (state.revision !== previewRevision) location.reload();
  let warning = document.getElementById('preview-sync-warning');
  if (state.error && !warning) {
    warning = document.createElement('p'); warning.id = 'preview-sync-warning';
    warning.style.cssText = 'padding:12px;color:#bd641d;text-align:center;font-size:13px';
    document.querySelector('.footer').append(warning);
  }
  if (warning) warning.textContent = state.error ? '本机同步暂不可用，当前保留上次报告：' + state.error : '';
}, 30000);
</script>'''.replace('REVISION', str(state['revision']))
                data = report.read_text(encoding='utf-8').replace('</body>', script + '</body>').encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                super().do_GET()

    threading.Thread(target=sync, daemon=True).start()
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(directory))).serve_forever()


if __name__ == '__main__':
    main()
