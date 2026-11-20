"""HTTP execution backed by requests, with timeout and one-shot timer."""
import time
import requests
from .variable import VariableContext


class HttpClient:
    def __init__(self, base_url="", timeout=5, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def execute(self, case, ctx: VariableContext):
        req = case.request
        url = ctx.render(req.url)
        url = url if url.startswith("http") else self.base_url + url
        headers = ctx.render_obj(req.headers or {})
        params = ctx.render_obj(req.params or {}) or None
        body = ctx.render_obj(req.body)
        # never log full Authorization token
        safe_headers = {k: ("***" if k.lower() == "authorization" else v) for k, v in headers.items()}
        start = time.perf_counter()
        try:
            resp = self.session.request(
                req.method, url, headers=headers, params=params,
                json=body if isinstance(body, (dict, list)) else None,
                data=body if isinstance(body, str) else None,
                timeout=self.timeout,
            )
            elapsed = int((time.perf_counter() - start) * 1000)
            try:
                body_json = resp.json()
            except Exception:
                body_json = None
            return {"status": resp.status_code, "text": resp.text, "json": body_json,
                    "ms": elapsed, "headers": safe_headers, "error": ""}
        except Exception as exc:
            elapsed = int((time.perf_counter() - start) * 1000)
            return {"status": 0, "text": "", "json": None, "ms": elapsed,
                    "headers": safe_headers, "error": str(exc)[:200]}
