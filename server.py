#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猜動漫歌 — 本地伺服器
- 僅提供白名單內的前端靜態檔案（index.html, config.js, config.example.js）
- /graphql   把 GraphQL POST 請求代理到 https://graphql.animethemes.moe/（含記憶體快取）
- /api/...   把 JSON 請求代理到 https://api.animethemes.moe/...（含記憶體快取）
- /media?u= 把音檔代理回來（嚴格驗證協定、網域與重新導向目標）
- 啟動後自動開瀏覽器
只用 Python 標準庫，不需要 pip 安裝任何東西。
"""

import http.server
import socketserver
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
import os
import threading
import webbrowser

GQL_URL = "https://graphql.animethemes.moe/"
API_HOST = "https://api.animethemes.moe"
START_PORT = 8753
HERE = os.path.dirname(os.path.abspath(__file__))
UA = "tanime-local-quiz/1.1 (personal use; https://animethemes.moe)"

ALLOWED_STATIC = {"/index.html", "/config.js", "/config.example.js"}

_cache = {}
_cache_lock = threading.Lock()


def _media_host_ok(host: str) -> bool:
    host = (host or "").lower().rstrip(".")
    return host == "animethemes.moe" or host.endswith(".animethemes.moe")


def _media_url_ok(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("https", "http") and _media_host_ok(parsed.hostname)
    except Exception:
        return False


class _SafeMediaRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _media_url_ok(newurl):
            raise urllib.error.HTTPError(newurl, 403, "redirect host not allowed", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_media_opener = urllib.request.build_opener(_SafeMediaRedirectHandler)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, *a):
        pass

    def _cors_origin(self):
        origin = self.headers.get("Origin") or ""
        try:
            p = urlparse(origin)
            if p.scheme in ("http", "https") and p.hostname in ("localhost", "127.0.0.1"):
                return origin
        except Exception:
            pass
        return f"http://localhost:{self.server.server_address[1]}"

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

    def do_POST(self):
        path_only = urlparse(self.path).path
        if path_only == "/graphql":
            self.proxy_graphql()
        else:
            self._send_simple(404, b"not found", "text/plain; charset=utf-8")

    def do_GET(self):
        parsed = urlparse(self.path)
        path_only = parsed.path

        if path_only.startswith("/api/"):
            self.proxy_api()
        elif path_only == "/media":
            self.proxy_media()
        else:
            if path_only in ("/", "", "/game.html"):
                self.path = "/index.html"
                path_only = "/index.html"
            if path_only not in ALLOWED_STATIC:
                self._send_simple(404, b"not found", "text/plain; charset=utf-8")
                return
            if path_only == "/config.js" and not os.path.exists(os.path.join(HERE, "config.js")):
                self._send_simple(200, b"window.APP_CONFIG = window.APP_CONFIG || {};\n", "application/javascript; charset=utf-8")
                return
            super().do_GET()

    # ---- GraphQL Proxy (cached) ----
    def proxy_graphql(self):
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            length = 0
        if length <= 0 or length > 65536:
            self._send_simple(400, b"invalid payload length", "text/plain; charset=utf-8")
            return
        req_body = self.rfile.read(length)
        cache_key = ("GQL", req_body)
        with _cache_lock:
            hit = _cache.get(cache_key)
        if hit:
            body, ctype = hit
        else:
            try:
                req = urllib.request.Request(
                    GQL_URL,
                    data=req_body,
                    headers={
                        "User-Agent": UA,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=20) as r:
                    body = r.read()
                    ctype = r.headers.get("Content-Type", "application/json")
                with _cache_lock:
                    if len(_cache) > 400:
                        _cache.clear()
                    _cache[cache_key] = (body, ctype)
            except urllib.error.HTTPError as e:
                self._send_simple(e.code, e.read(), "application/json")
                return
            except Exception as e:
                self._send_simple(502, ("proxy error: " + str(e)).encode("utf-8"), "text/plain; charset=utf-8")
                return
        self._send_head(200, ctype)
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ---- JSON API (cached) ----
    def proxy_api(self):
        suffix = self.path[len("/api"):]
        if not suffix.startswith("/"):
            self._send_simple(400, b"invalid api path", "text/plain; charset=utf-8")
            return
        target = API_HOST + suffix
        with _cache_lock:
            hit = _cache.get(target)
        if hit:
            body, ctype = hit
        else:
            try:
                req = urllib.request.Request(
                    target, headers={"User-Agent": UA, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    body = r.read()
                    ctype = r.headers.get("Content-Type", "application/json")
                with _cache_lock:
                    if len(_cache) > 400:
                        _cache.clear()
                    _cache[target] = (body, ctype)
            except urllib.error.HTTPError as e:
                self._send_simple(e.code, e.read(), "application/json")
                return
            except Exception as e:
                self._send_simple(502, ("proxy error: " + str(e)).encode("utf-8"), "text/plain; charset=utf-8")
                return
        self._send_head(200, ctype)
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ---- media passthrough (streamed, not cached) ----
    def proxy_media(self):
        qs = parse_qs(urlparse(self.path).query)
        u = (qs.get("u") or [None])[0]
        if not u:
            self._send_simple(400, b"missing u", "text/plain; charset=utf-8")
            return
        if not _media_url_ok(u):
            self._send_simple(400, b"url not allowed", "text/plain; charset=utf-8")
            return
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with _media_opener.open(req, timeout=30) as r:
                ctype = r.headers.get("Content-Type", "application/octet-stream")
                clen = r.headers.get("Content-Length")
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Access-Control-Allow-Origin", self._cors_origin())
                self.send_header("X-Content-Type-Options", "nosniff")
                if clen:
                    self.send_header("Content-Length", clen)
                self.end_headers()
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except urllib.error.HTTPError as e:
            self._send_simple(e.code, b"media http error", "text/plain; charset=utf-8")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self._send_simple(502, ("media error: " + str(e)).encode("utf-8"), "text/plain; charset=utf-8")

    def _send_head(self, code, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send_simple(self, code, body, ctype):
        try:
            self._send_head(code, ctype)
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


class ReuseTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def find_port(start):
    import socket
    for p in range(start, start + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start


def main():
    port = find_port(START_PORT)
    url = f"http://localhost:{port}/"
    httpd = ReuseTCPServer(("127.0.0.1", port), Handler)
    print("=" * 46)
    print("  tanime 猜動漫歌  已啟動")
    print("  Game running at: " + url)
    print("  關閉這個視窗即可結束遊戲。")
    print("=" * 46)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()
