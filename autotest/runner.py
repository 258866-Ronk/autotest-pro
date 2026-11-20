"""Execution engine: dependency-aware sequential / parallel groups."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import CaseResult, Assertion
from .assertions import evaluate
from .variable import VariableContext


def needs_sequential(case) -> bool:
    if case.extract:
        return True
    req = case.request
    if VariableContext.has_var(req.url, req.headers, req.params, req.body):
        return True
    for a in case.assertions:
        if VariableContext.has_var(str(a.expected), a.path):
            return True
    if any(VariableContext.has_var(v) for v in case.variables.values()):
        return True
    return False


def _run_one(case, client, ctx):
    response = client.execute(case, ctx)
    if response["error"]:
        return CaseResult(case.name, False, 0, response["ms"], [], response["error"])
    # render variable placeholders inside assertions (e.g. expected: ${orderId})
    rendered_assertions = [
        Assertion(a.type, ctx.render(a.path), a.op, ctx.render(a.expected))
        for a in case.assertions
    ]
    checks = evaluate(response["status"], response["text"], response["json"],
                      response["ms"], rendered_assertions)
    for var_name, path in case.extract.items():
        try:
            from .assertions import get_by_path
            ctx.set(var_name, get_by_path(response["json"], path))
        except Exception:
            ctx.set(var_name, None)
    passed = all(c.passed for c in checks)
    return CaseResult(case.name, passed, response["status"], response["ms"], checks, "")


def run(cases, client, base_ctx, mode="sequential", threads=4):
    results = []
    sequential = [c for c in cases if needs_sequential(c)]
    parallel = [c for c in cases if not needs_sequential(c)]

    ctx = base_ctx
    for case in sequential:
        results.append(_run_one(case, client, ctx))

    if parallel:
        if mode == "parallel":
            with ThreadPoolExecutor(max_workers=threads) as pool:
                futures = {pool.submit(_run_one, c, client, base_ctx.child()): c for c in parallel}
                for fut in as_completed(futures):
                    results.append(fut.result())
        else:
            for case in parallel:
                results.append(_run_one(case, client, base_ctx.child()))
    return results
