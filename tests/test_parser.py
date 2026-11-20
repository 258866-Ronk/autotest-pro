import os
from autotest.parser import load_cases, expand_data


def test_load_and_expand(tmp_path):
    tc = tmp_path / "testcases"
    tc.mkdir()
    (tc / "data").mkdir()
    (tc / "data" / "u.csv").write_text("user\np1\np2\n", encoding="utf-8")
    (tc / "a.yaml").write_text(
        "name: A\nrequest:\n  method: GET\n  url: /x\n"
        "assertions:\n  - type: status_code\n    op: eq\n    expected: 200\n",
        encoding="utf-8")
    (tc / "b.yaml").write_text(
        "name: B\nrequest:\n  method: GET\n  url: /y\ndataSource: data/u.csv\n",
        encoding="utf-8")
    cases = load_cases(str(tc))
    assert len(cases) == 2
    expanded = expand_data(cases, str(tc))
    assert len(expanded) == 3
