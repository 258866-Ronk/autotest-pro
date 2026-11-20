"""Safe YAML testcase loader (safe_load only, no object construction)."""
import os, csv
import yaml
from .models import TestCase, RequestConfig, Assertion


def load_case_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    req = data.get("request") or {}
    return TestCase(
        name=data.get("name") or os.path.basename(path),
        description=data.get("description", ""),
        request=RequestConfig(
            method=req.get("method", "GET").upper(),
            url=req.get("url", ""),
            headers=req.get("headers") or {},
            params=req.get("params") or {},
            body=req.get("body"),
        ),
        assertions=[Assertion(**a) for a in (data.get("assertions") or [])],
        extract=data.get("extract") or {},
        variables=data.get("variables") or {},
        data_source=data.get("dataSource") or data.get("data_source") or "",
        tags=data.get("tags") or [],
    )


def load_cases(testcase_dir):
    cases = []
    for name in sorted(os.listdir(testcase_dir)):
        if name.endswith((".yaml", ".yml")):
            cases.append(load_case_file(os.path.join(testcase_dir, name)))
    return cases


def expand_data(cases, testcase_dir):
    """Expand CSV-driven cases into one concrete case per CSV row."""
    expanded = []
    for case in cases:
        if not case.data_source:
            expanded.append(case)
            continue
        csv_path = os.path.join(testcase_dir, case.data_source)
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as fh:
            for idx, row in enumerate(csv.DictReader(fh), 1):
                vars_copy = dict(case.variables)
                vars_copy.update(row)
                expanded.append(TestCase(
                    name=f"{case.name}[row{idx}]",
                    description=case.description,
                    request=case.request,
                    assertions=case.assertions,
                    extract=case.extract,
                    variables=vars_copy,
                    tags=case.tags,
                ))
    return expanded


def load_environment(path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
