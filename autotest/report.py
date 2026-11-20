"""JSON + HTML report generator. All numbers come from real measurements."""
import json, html


def _esc(s):
    return html.escape(str(s), quote=True)


def write_json(summary, path):
    payload = {
        "runId": summary.run_id, "environment": summary.environment,
        "baseUrl": summary.base_url, "startedAt": summary.started_at,
        "durationMs": summary.duration_ms, "total": summary.total,
        "passed": summary.passed, "failed": summary.failed,
        "passRate": summary.pass_rate,
        "cases": [{
            "name": r.name, "passed": r.passed, "statusCode": r.status_code,
            "responseTimeMs": r.response_time_ms, "error": r.error,
            "assertions": [{"type": a.type, "path": a.path, "op": a.op,
                            "expected": a.expected, "actual": a.actual, "passed": a.passed}
                           for a in r.assertions],
        } for r in summary.results],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def write_html(summary, path):
    rows = []
    for r in summary.results:
        badge = "PASS" if r.passed else "FAIL"
        cls = "pass" if r.passed else "fail"
        asserts = "".join(
            "<div class='as'><b>%s</b> %s %s &rarr; expected <code>%s</code>, actual <code>%s</code></div>"
            % (_esc(a.type), _esc(a.path), _esc(a.op), _esc(a.expected), _esc(a.actual))
            for a in r.assertions)
        rows.append("<tr><td>%s</td><td class='%s'>%s</td><td>%s</td><td>%d ms</td><td>%s</td></tr>"
                    % (_esc(r.name), cls, badge, r.status_code, r.response_time_ms,
                       asserts or _esc(r.error)))
    doc = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>AutoTest Pro Report</title><style>
body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:32px;color:#1f2937}
h1{color:#1b4d3e} .meta{color:#6b7280;margin-bottom:20px}
.cards{display:flex;gap:14px;margin-bottom:24px}
.card{background:#f3f7f4;border:1px solid #d6e2da;border-radius:10px;padding:16px 22px}
.card b{display:block;font-size:28px;color:#1b4d3e}
table{border-collapse:collapse;width:100%%;font-size:13px}
th,td{border:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}
th{background:#f9fafb} .pass{color:#1b7a4b;font-weight:700} .fail{color:#b91c1c;font-weight:700}
.as{color:#4b5563;padding:2px 0} code{background:#f3f4f6;padding:1px 4px;border-radius:4px}
</style></head><body><h1>AutoTest Pro · 测试报告</h1>
<div class="meta">Run @@RUN@@ · 环境 @@ENV@@ · @@BASE@@ · 开始 @@START@@</div>
<div class="cards"><div class="card">用例<b>@@TOTAL@@</b></div>
<div class="card">通过<b>@@PASSED@@</b></div><div class="card">失败<b>@@FAILED@@</b></div>
<div class="card">通过率<b>@@RATE@@%%</b></div><div class="card">耗时<b>@@DURATION@@ ms</b></div></div>
<table><thead><tr><th>用例</th><th>结果</th><th>状态码</th><th>响应</th><th>断言明细</th></tr></thead>
<tbody>@@ROWS@@</tbody></table></body></html>"""
    return (doc.replace("@@RUN@@", _esc(summary.run_id))
               .replace("@@ENV@@", _esc(summary.environment))
               .replace("@@BASE@@", _esc(summary.base_url))
               .replace("@@START@@", _esc(summary.started_at))
               .replace("@@TOTAL@@", str(summary.total))
               .replace("@@PASSED@@", str(summary.passed))
               .replace("@@FAILED@@", str(summary.failed))
               .replace("@@RATE@@", str(summary.pass_rate))
               .replace("@@DURATION@@", str(summary.duration_ms))
               .replace("@@ROWS@@", "".join(rows)))


def write_all(summary, out_dir):
    import os
    os.makedirs(out_dir, exist_ok=True)
    write_json(summary, os.path.join(out_dir, "report.json"))
    with open(os.path.join(out_dir, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(write_html(summary, os.path.join(out_dir, "report.html")))
