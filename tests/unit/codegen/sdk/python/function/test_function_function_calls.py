from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.python import PyFunction


def test_function_calls(tmpdir) -> None:
    # language=python
    content = """
def foo():
    a(1, 2)
    b = c('3')
    return d(arg=4)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        function_symbol = file.get_function("foo")
        assert len(function_symbol.function_calls) == 3

        # First Call
        assert function_symbol.function_calls[0].source == "a(1, 2)"
        assert function_symbol.function_calls[0].name == "a"

        # Second Call
        assert function_symbol.function_calls[1].source == "c('3')"
        assert function_symbol.function_calls[1].name == "c"

        # Third Call
        assert function_symbol.function_calls[2].source == "d(arg=4)"
        assert function_symbol.function_calls[2].name == "d"


def test_function_calls_and_arguments(tmpdir) -> None:
    # language=python
    content = """
from a.b import (c as d, e as f)

def foo(tmpdir):  # none returned
    return 5

def bar(x, y, z):  # trivial case
    return foo(1, 2)

def bar2(x, y, z):  # composition
    x = foo() + bar()
    y = foo(bar())

def baz(tmpdir):  # less trivial - includes composition etc.
    if True:
        return f(1, 2, 3)  # simple case
    else:
        return d(f(1, 2, 3), 5, 6)

"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # =====[ foo - none returned ]=====
        f: PyFunction = file.get_function("foo")
        calls = f.function_calls
        assert len(calls) == 0

        # =====[ bar - one returned ]=====
        g: PyFunction = file.get_function("bar")
        calls = g.function_calls
        assert len(calls) == 1
        call = calls[0]
        assert call.name == "foo"
        assert len(call.args) == 2

        # =====[ bar2 - composition ]=====
        h: PyFunction = file.get_function("bar2")
        calls = h.function_calls
        assert len(calls) == 4
        call = calls[0]
        assert call.name == "foo"
        assert len(call.args) == 0
        call = calls[1]
        assert call.name == "bar"
        assert len(call.args) == 0
        call = calls[2]
        assert call.name == "foo"
        assert len(call.args) == 1
        call = calls[3]
        assert call.name == "bar"
        assert len(call.args) == 0
