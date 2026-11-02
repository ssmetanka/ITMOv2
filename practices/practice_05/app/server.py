from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import mimetypes
from urllib.parse import parse_qs, urlparse

from app.api import Api


class Handler(BaseHTTPRequestHandler):
    api = Api()
    ui_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")

    def _set_headers(self, code: int, content_type: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def _serve_static(self, path: str) -> bool:
        # Map "/" to "/ui/index.html" and "/ui" to "/ui/index.html"
        if path == "/" or path == "/ui" or path == "/ui/":
            rel = "index.html"
            base = self.ui_root
        elif path.startswith("/ui/"):
            rel = path[len("/ui/") :]
            base = self.ui_root
        else:
            return False

        # Prevent path traversal
        safe_root = os.path.abspath(base)
        requested = os.path.abspath(os.path.join(base, rel))
        if not requested.startswith(safe_root):
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}}).encode())
            return True

        if not os.path.isfile(requested):
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}}).encode())
            return True

        ctype, _ = mimetypes.guess_type(requested)
        ctype = ctype or "application/octet-stream"
        self._set_headers(200, ctype)
        with open(requested, "rb") as f:
            self.wfile.write(f.read())
        return True

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        # Static UI first (no /api prefix)
        if not parsed.path.startswith("/api/"):
            if self._serve_static(parsed.path):
                return
        if parsed.path == "/api/limits":
            self._set_headers(200)
            self.wfile.write(json.dumps(self.api.get_limits()).encode())
            return
        if parsed.path == "/api/reviews":
            qs = parse_qs(parsed.query)
            limit = None
            if "limit" in qs:
                try:
                    limit = int(qs["limit"][0])
                except Exception:
                    limit = None
            code, body = self.api.list_reviews(limit)
            self._set_headers(code)
            self.wfile.write(json.dumps(body).encode())
            return
        if parsed.path.startswith("/api/reviews/"):
            review_id = parsed.path.split("/api/reviews/")[-1]
            code, body = self.api.get_review(review_id)
            self._set_headers(code)
            self.wfile.write(json.dumps(body).encode())
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}}).encode())

    def do_POST(self):  # noqa: N802
        if self.path == "/api/reviews":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = self.rfile.read(length)
                payload = json.loads(data.decode())
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": {"code": "INVALID_REQUEST", "message": "Invalid JSON", "details": {}}}).encode())
                return
            code, body = self.api.create_review(payload)
            self._set_headers(code)
            self.wfile.write(json.dumps(body).encode())
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}}).encode())


def serve(port: int = 8000):
    server = ThreadingHTTPServer(("", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    srv, t = serve(args.port)
    try:
        t.join()
    except KeyboardInterrupt:
        pass
    finally:
        srv.shutdown()
