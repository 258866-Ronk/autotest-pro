from autotest.models import TestCase, RequestConfig, Assertion
from autotest.variable import VariableContext
from autotest.runner import needs_sequential


def test_dependency_detection():
    chain = TestCase("chain", request=RequestConfig("GET", "/${id}"))
    assert needs_sequential(chain)
    independent = TestCase("free", request=RequestConfig("GET", "/health"))
    assert not needs_sequential(independent)
