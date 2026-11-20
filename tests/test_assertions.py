from autotest.assertions import get_by_path, evaluate
from autotest.models import Assertion


def test_json_path():
    assert get_by_path({"data": {"token": "t"}}, "$.data.token") == "t"
    assert get_by_path({"data": [{"id": 7}]}, "$.data[0].id") == 7


def test_numeric_equality():
    rs = evaluate(200, "", {}, 10, [Assertion("status_code", "", "eq", 200)])
    assert rs[0].passed


def test_response_time():
    rs = evaluate(200, "", {}, 15, [Assertion("response_time", "", "lt", 20)])
    assert rs[0].passed
