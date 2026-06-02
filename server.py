#!/usr/bin/env python3
import json, os, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

SCORES_FILE = os.path.join(os.path.dirname(__file__), 'scores.json')
lock = threading.Lock()

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE) as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def log_message(self, fmt, *args):
        pass  # quiet

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/scores':
            with lock:
                scores = load_scores()
            scores.sort(key=lambda x: x['score'], reverse=True)
            self.send_json(200, scores[:20])
        else:
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/scores':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                entry = json.loads(body)
                name = str(entry.get('name', 'Anonymous')).strip()[:20] or 'Anonymous'
                score = int(entry.get('score', 0))
                if score < 0:
                    raise ValueError
            except Exception:
                self.send_json(400, {'error': 'bad request'})
                return
            with lock:
                scores = load_scores()
                # Update existing player's best score, or add new entry
                for s in scores:
                    if s['name'].lower() == name.lower():
                        if score > s['score']:
                            s['score'] = score
                        self.send_json(200, {'ok': True, 'best': s['score']})
                        save_scores(scores)
                        return
                scores.append({'name': name, 'score': score})
                save_scores(scores)
            self.send_json(200, {'ok': True, 'best': score})
        else:
            self.send_json(404, {'error': 'not found'})

if __name__ == '__main__':
    port = 8765
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'🍑 Tap the Butt server running on http://0.0.0.0:{port}')
    server.serve_forever()
