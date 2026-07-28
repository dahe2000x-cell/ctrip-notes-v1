#!/usr/bin/env python3
"""携程笔记工作台 同步后端服务"""
import http.server
import json
import os
import cgi
from io import BytesIO

DIR = os.path.dirname(os.path.abspath(__file__))

class SyncHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save-topics':
            self._save_json('topics.json')
        elif self.path == '/api/save-images':
            self._save_json('images.json')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')

    def _save_json(self, filename):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            filepath = os.path.join(DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print(f'[SYNC] {filename} saved ({len(data)} items)')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = http.server.HTTPServer(('0.0.0.0', port), SyncHandler)
    print(f'[携程笔记工作台] http://0.0.0.0:{port}')
    server.serve_forever()
