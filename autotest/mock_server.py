"""Dependency-free Mock API server using the standard library."""
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

TOK = "mock-token-abc123"


class MockAPI:
    def __init__(self, port=0):
        self.orders = {}
        self.server = ThreadingHTTPServer(("127.0.0.1", port), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _handler(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, code, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _json_body(self):
                try:
                    n = int(self.headers.get("Content-Length", 0))
                    return json.loads(self.rfile.read(n) or b"{}")
                except Exception:
                    return {}

            def do_GET(self):
                path = urlparse(self.path).path
                if path == "/health":
                    return self._send(200, {"status": "UP"})
                if path == "/api/products":
                    return self._send(200, {"data": [{"id": 1, "name": "keyboard", "price": 199},
                                                      {"id": 2, "name": "mouse", "price": 99}]})
                if path.startswith("/api/orders/"):
                    oid = path.rsplit("/", 1)[-1]
                    order = outer.orders.get(oid)
                    return self._send(200, {"data": order}) if order else self._send(404, {"msg": "not found"})
                return self._send(404, {"msg": "not found"})

            def do_POST(self):
                path = urlparse(self.path).path
                body = self._json_body()
                if path == "/api/login":
                    if body.get("username") and body.get("password"):
                        return self._send(200, {"data": {"token": TOK, "user": body["username"]}})
                    return self._send(400, {"msg": "missing credentials"})
                if path == "/api/orders":
                    if self.headers.get("Authorization") != "Bearer " + TOK:
                        return self._send(401, {"msg": "unauthorized"})
                    oid = "ORD" + str(len(outer.orders) + 1).zfill(4)
                    order = {"id": oid, "amount": body.get("amount", 0), "status": "CREATED"}
                    outer.orders[oid] = order
                    return self._send(200, {"data": order})
                return self._send(404, {"msg": "not found"})

        return Handler

    @property
    def port(self):
        return self.server.server_address[1]

    @property
    def base_url(self):
        return "http://127.0.0.1:%d" % self.port

    def start(self):
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
