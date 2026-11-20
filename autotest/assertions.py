"""Structured assertion engine with a small JSONPath reader."""
import re
from decimal import Decimal, InvalidOperation
from typing import Any
from .models import Assertion, AssertionResult, CaseResult

SEG = re.compile(r"[^.\[\]]+|\[\d+\]")


def get_by_path(obj: Any, path: str) -> Any:
    if not path:
        return obj
    cleaned = path[2:] if path.startswith("$.") else (path[1:] if path.startswith("$") else path)
    cur = obj
    for seg in SEG.findall(cleaned):
        if seg.startswith("[") and seg.endswith("]"):
            cur = cur[int(seg[1:-1])]
        elif isinstance(cur, dict):
            cur = cur[seg]
        else:
            raise KeyError(seg)
    return cur


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _compare(actual, expected, op):
    if op == "eq":
        da, de = _to_decimal(actual), _to_decimal(expected)
        if da is not None and de is not None:
            return da == de
        return str(actual) == str(expected)
    if op == "ne":
        return not _compare(actual, expected, "eq")
    if op in ("gt", "gte", "lt", "lte"):
        da, de = _to_decimal(actual), _to_decimal(expected)
        if da is None or de is None:
            return False
        return {"gt": da > de, "gte": da >= de, "lt": da < de, "lte": da <= de}[op]
    if op == "contains":
        return str(expected) in str(actual)
    if op == "not_null":
        return actual is not None
    raise ValueError("unsupported op: " + op)


def evaluate(status_code, body_text, body_json, response_ms, assertions):
    results = []
    for a in assertions:  # type: Assertion
        if a.type == "status_code":
            actual, ok = status_code, _compare(status_code, a.expected, a.op)
        elif a.type == "json_path":
            try:
                actual = get_by_path(body_json, a.path)
                ok = _compare(actual, a.expected, a.op)
            except Exception as exc:
                actual, ok = "PATH_NOT_FOUND: " + str(exc), False
        elif a.type == "body_contains":
            actual, ok = body_text, _compare(body_text, a.expected, "contains")
        elif a.type == "response_time":
            actual, ok = response_ms, _compare(response_ms, a.expected, a.op)
        else:
            actual, ok = None, False
        results.append(AssertionResult(a.type, a.path, a.op, a.expected, actual, bool(ok)))
    return results
