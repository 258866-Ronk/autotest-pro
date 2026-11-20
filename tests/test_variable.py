from autotest.variable import VariableContext


def test_render_known():
    c = VariableContext({"token": "abc"})
    assert c.render("Bearer ${token}") == "Bearer abc"


def test_render_unknown_is_kept():
    c = VariableContext({})
    assert c.render("${missing}") == "${missing}"


def test_parent_inheritance():
    root = VariableContext({"a": "1"})
    child = root.child()
    assert child.get("a") == "1"
    child.set("b", "2")
    assert root.get("b") is None


def test_has_var():
    assert VariableContext.has_var("x ${y}")
    assert not VariableContext.has_var("plain")
