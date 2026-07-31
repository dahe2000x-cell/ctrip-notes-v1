#!/usr/bin/env python3
"""携程笔记工作台 完整后端服务 - 支持 GET 静态文件 + POST 修改笔记"""
import http.server
import json
import os
import re

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
        if self.path == '/api/fix-note':
            self._fix_note()
        elif self.path == '/api/request-fix':
            self._request_fix()
        elif self.path == '/api/save-topics':
            self._save_json('topics.json')
        elif self.path == '/api/save-images':
            self._save_json('images.json')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({"error":"not found"}).encode())

    def _fix_note(self):
        """修改单篇笔记: {date, idx, field, value}"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            date = body.get('date', '')
            idx = body.get('idx', 0)
            field = body.get('field', '')
            value = body.get('value', '')

            filename = f'notes_{date}.json'
            filepath = os.path.join(DIR, filename)

            if not os.path.exists(filepath):
                self._json_resp(404, {"error": f"文件不存在: {filename}"})
                return

            with open(filepath, 'r', encoding='utf-8') as f:
                posts = json.load(f)

            # 找到对应篇
            target = None
            for p in posts:
                if p.get('idx') == idx:
                    target = p
                    break

            if not target:
                self._json_resp(404, {"error": f"找不到 idx={idx}"})
                return

            # 允许修改的字段
            allowed = ['city', 'imageTitle', 'bodyTitle', 'body', 'tags', 'strength']
            if field not in allowed:
                self._json_resp(400, {"error": f"不允许修改字段: {field}"})
                return

            target[field] = value
            if field == 'body':
                target['words'] = len(value)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)

            # 如果是 today_notes.json 对应的日期，同步更新
            today_file = os.path.join(DIR, 'today_notes.json')
            if os.path.exists(today_file):
                with open(today_file, 'r') as f:
                    today_posts = json.load(f)
                if isinstance(today_posts, list) and len(today_posts) > 0:
                    for tp in today_posts:
                        if tp.get('idx') == idx:
                            tp[field] = value
                            if field == 'body':
                                tp['words'] = len(value)
                            break
                    with open(today_file, 'w') as f:
                        json.dump(today_posts, f, ensure_ascii=False, indent=2)

            new_words = len(target.get('body', ''))
            self._json_resp(200, {
                "ok": True,
                "city": target['city'],
                "field": field,
                "words": new_words
            })
        except Exception as e:
            self._json_resp(500, {"error": str(e)})

    def _request_fix(self):
        """AI修改请求队列: {date, idx, city, issue, account}"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            import time
            req_file = os.path.join(DIR, 'fix_requests.json')
            reqs = json.load(open(req_file)) if os.path.exists(req_file) else []
            reqs.append({
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "date": body.get('date',''),
                "idx": body.get('idx',0),
                "city": body.get('city',''),
                "account": body.get('account',''),
                "issue": body.get('issue',''),
                "status": "pending"
            })
            with open(req_file, 'w', encoding='utf-8') as f:
                json.dump(reqs, f, ensure_ascii=False, indent=2)
            self._json_resp(200, {"ok": True, "message": "已提交"})
        except Exception as e:
            self._json_resp(500, {"error": str(e)})

    def _save_json(self, filename):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            filepath = os.path.join(DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._json_resp(200, {"ok": True, "count": len(data)})
        except Exception as e:
            self._json_resp(500, {"error": str(e)})

    def _json_resp(self, code, data):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = http.server.HTTPServer(('0.0.0.0', port), SyncHandler)
    print(f'[携程笔记] http://0.0.0.0:{port}')
    server.serve_forever()
