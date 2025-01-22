from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.core.external_module import ExternalModule


def test_function_call_graph_successors(tmpdir) -> None:
    # language=python
    content = """
def f(tmpdir):
    pass

def g(tmpdir):
    return f()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        f = file.get_function("f")
        g = file.get_function("g")
        call_graph_successors = g.call_graph_successors()
        function_call = call_graph_successors[0].call
        function_called = call_graph_successors[0].callables[0]
        assert len(call_graph_successors) == 1
        assert function_called == f
        assert function_call.source == "f()"
        assert list(function_call.line_range) == [5]


def test_function_multiple_call_graph_successors(tmpdir) -> None:
    # language=python
    content = """
def f1(tmpdir):
    pass

def f2(tmpdir):
    pass

def f3(tmpdir):
    pass

def g(tmpdir):
    return f1() + f2() + f3()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        g = file.get_function("g")
        call_graph_successors = g.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(call_graph_successors) == 3
        assert set(functions_called) == {file.get_function("f1"), file.get_function("f2"), file.get_function("f3")}
        assert function_calls[0].source == "f1()"
        assert function_calls[1].source == "f2()"
        assert function_calls[2].source == "f3()"
        assert list(function_calls[0].line_range) == [11]


def test_function_class_call_graph_successors(tmpdir) -> None:
    # language=python
    content = """
class A():
    pass

class B():
    def __init__(self):
        pass

def foo():
    a = A()
    b = B()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        call_graph_successors = foo.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert set(functions_called) == {file.get_class("A"), file.get_class("B").get_method("__init__")}
        assert len(call_graph_successors) == 2
        assert function_calls[0].source == "A()"
        assert function_calls[1].source == "B()"
        assert list(function_calls[0].line_range) == [9]
        assert list(function_calls[1].line_range) == [10]

        call_graph_successors2 = foo.call_graph_successors(include_classes=False)
        function_calls2 = [call_graph_successor.call for call_graph_successor in call_graph_successors2]
        functions_called2 = [callable for call_graph_successor in call_graph_successors2 for callable in call_graph_successor.callables]
        assert len(call_graph_successors2) == 1
        assert functions_called2[0] == file.get_class("B").get_method("__init__")
        assert function_calls2[0].source == "B()"
        assert list(function_calls2[0].line_range) == [10]


def test_function_ext_call_graph_successors(tmpdir) -> None:
    # language=python
    content = """
from a import b

def foo():
    thing = b()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        call_graph_successors = foo.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(call_graph_successors) == 1
        assert isinstance(functions_called[0], ExternalModule)
        assert functions_called[0].name == "b"
        assert function_calls[0].source == "b()"
        assert list(function_calls[0].line_range) == [4]

        call_graph_successors2 = foo.call_graph_successors(include_external=False)
        assert len(call_graph_successors2) == 0
