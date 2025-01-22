import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.external_module import ExternalModule
from graph_sitter.enums import ProgrammingLanguage


def test_function_call_graph_successors(tmpdir) -> None:
    # language=typescript
    content = """
function f() {
    return;
}

function g() {
    return f();
}
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        f = file.get_function("f")
        g = file.get_function("g")
        call_graph_successors = g.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(function_calls) == 1
        assert list(function_calls[0].line_range) == [6]
        assert functions_called[0] == f


def test_function_multiple_call_graph_successors(tmpdir) -> None:
    # language=typescript
    content = """
function f1() {
    return;
}

function f2() {
    return;
}

function f3() {
    return;
}

function g() {
    return f1(), f2(), f3();
}
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        g = file.get_function("g")
        call_graph_successors = g.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(function_calls) == 3
        assert list(function_calls[0].line_range) == [14]
        assert list(function_calls[1].line_range) == [14]
        assert list(function_calls[2].line_range) == [14]
        assert set(functions_called) == {file.get_function("f1"), file.get_function("f2"), file.get_function("f3")}


@pytest.mark.skip("TODO: Classes not in function calls for some reason. TODO @edward")
def test_function_class_call_graph_successors(tmpdir) -> None:
    # language=typescript
    content = """
class A {
    constructor() {}
}

class B {
    constructor() {}
}

function foo() {
    const a = new A();
    const b = new B();
}
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        foo = file.get_function("foo")

        call_graph_successors = foo.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(function_calls) == 2
        assert list(function_calls[0].line_range) == [10]
        assert list(function_calls[1].line_range) == [11]
        assert set(functions_called) == {file.get_class("A").constructor, file.get_class("B").constructor}

        call_graph_successors2 = foo.call_graph_successors(include_classes=False)
        function_calls2 = [call_graph_successor.call for call_graph_successor in call_graph_successors2]
        functions_called2 = [callable for call_graph_successor in call_graph_successors2 for callable in call_graph_successor.callables]
        assert len(function_calls2) == 1
        assert list(function_calls2[0].line_range) == [14]
        assert set(functions_called2) == {file.get_class("B").constructor}


def test_function_ext_call_graph_successors(tmpdir) -> None:
    # language=typescript
    content = """
import { b } from 'a';

function foo() {
    const thing = b();
}
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as codebase:
        file = codebase.get_file("test.ts")
        foo = file.get_function("foo")

        call_graph_successors = foo.call_graph_successors()
        function_calls = [call_graph_successor.call for call_graph_successor in call_graph_successors]
        functions_called = [callable for call_graph_successor in call_graph_successors for callable in call_graph_successor.callables]
        assert len(functions_called) == 1
        assert isinstance(functions_called[0], ExternalModule)
        assert functions_called[0].name == "b"
        assert list(function_calls[0].line_range) == [4]

        call_graph_successors2 = foo.call_graph_successors(include_external=False)
        assert len(call_graph_successors2) == 0
