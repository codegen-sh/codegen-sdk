import pytest

from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.core.expressions import String


@pytest.mark.skip(reason="CG-9463: Fix resolved types to be start byte aware")
def test_resolve_function_call_arg(tmpdir) -> None:
    # language=python
    content = """
def foo():
    a = 1
    a = 'hello'
    func_call(a)
    a = 'world'
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        func_call = file.get_function("foo").function_calls[0]
        arg_val = func_call.args[0].value
        arg_var = arg_val.resolved_value
        assert func_call.args[0].value == "a"
        assert isinstance(arg_var, String)
        assert arg_var.source == "'hello'"


@pytest.mark.skip(reason="CG-9463: Fix resolved types to be start byte aware")
def test_resolve_assignment_value(tmpdir) -> None:
    # language=python
    content = """
global_var = 1
a = x
global_var = a
b = global_var

var2 = 2
b = var2
var2 = b
c = var2
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        a = file.get_global_var("a")
        a_value = a.value.resolved_value
        assert a_value.source == "x"
        b = file.get_global_var("b")
        b_value = b.value.resolved_value
        assert b_value.source == "x"
        c = file.get_global_var("c")
        c_value = c.value.resolved_value
        assert c_value.source == "2"


@pytest.mark.skip(reason="CG-9463: Fix resolved types to be start byte aware")
def test_resolve_nested_value(tmpdir) -> None:
    # language=python
    content = """
def bar(x):
    return x

def foo(y):
    a = 1
    y = a
    if bar(a) == bar(y):
        return y
    elif bar(a) == 2:
        return a
    else:
        return 3
    return a
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        if_block = file.get_function("foo").code_block.if_blocks[0]
        fcalls = if_block.function_calls
        assert fcalls[0].args[0].value == "a"
        assert fcalls[0].args[0].value.resolved_value == "1"
        assert fcalls[1].args[0].value == "y"
        assert fcalls[1].args[0].value.resolved_value == "1"
        assert fcalls[2].args[0].value == "a"
        assert fcalls[2].args[0].value.resolved_value == "1"
