"""Zero-dependency local HTTP app. Run: python -m app.server"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .estimator import estimate, load_catalog

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'data' / 'catalog.csv'
HTML = ROOT / 'web' / 'index.html'


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, mime='application/json'):
        encoded = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', f'{mime}; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/qa-bench.html':
            return self.reply(200, (ROOT / 'web' / 'qa-bench.html').read_text(encoding='utf-8'), 'text/html')
        if route == '/':
            return self.reply(200, HTML.read_text(encoding='utf-8'), 'text/html')
        if route == '/api/catalog':
            catalog = load_catalog(CATALOG)
            return self.reply(200, json.dumps([{**v, 'material_unit_cost': str(v['material_unit_cost']), 'labor_hours_per_unit': str(v['labor_hours_per_unit'])} for v in catalog.values()]))
        if route == '/api/health':
            return self.reply(200, '{"status":"ok"}')
        return self.reply(404, '{"error":"Not found"}')

    def do_POST(self):
        if urlparse(self.path).path != '/api/estimate':
            return self.reply(404, '{"error":"Not found"}')
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > 100_000:
                return self.reply(413, '{"error":"Request size invalid"}')
            data = json.loads(self.rfile.read(size))
            result = estimate(data, load_catalog(CATALOG))
            return self.reply(200, json.dumps(result))
        except (ValueError, json.JSONDecodeError) as exc:
            return self.reply(400, json.dumps({'error': str(exc)}))
        except Exception:
            return self.reply(500, '{"error":"Internal server error"}')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', '8000'))
    print(f'Server running on port {port}')
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
