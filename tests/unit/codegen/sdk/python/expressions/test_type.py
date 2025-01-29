from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.expressions.none_type import NoneType
from codegen.sdk.core.expressions.type import Type
from codegen.sdk.python.expressions.union_type import PyUnionType

if TYPE_CHECKING:
    from codegen.sdk.python import PyAssignment, PyClass, PyFunction


def test_type_basic(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
def foo(a: int):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        foo = codebase.get_symbol("foo")
        annotation = foo.parameters[0].type
        assert isinstance(annotation, Type)
        assert annotation.source == "int"
        assert annotation.name == "int"
        assert not hasattr(annotation, "parameters")
        annotation.edit("str")
    # language=python
    assert (
        file.content
        == """
def foo(a: str):
    pass
"""
    )


def test_type_generic(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
def foo(a: tuple[int, int]):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        foo = codebase.get_symbol("foo")
        annotation = foo.parameters[0].type
        assert isinstance(annotation, Type)
        assert annotation.source == "tuple[int, int]"
        assert annotation.name == "tuple"
        assert len(annotation.parameters) == 2
        assert annotation.parameters[0] == "int"
        assert annotation.parameters[1] == "int"
        annotation.parameters.append("str")
    # language=python
    assert (
        file.content
        == """
def foo(a: tuple[int, int, str]):
    pass
"""
    )


def test_type_union(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
def foo(a: int | None):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        foo = codebase.get_symbol("foo")
        annotation = foo.parameters[0].type
        assert isinstance(annotation, PyUnionType)
        assert annotation.source == "int | None"
        assert len(annotation) == 2
        assert annotation[0] == "int"
        assert isinstance(annotation[1], NoneType)
        annotation.append("str")
    # language=python
    assert (
        file.content
        == """
def foo(a: int | None | str):
    pass
"""
    )


def test_type_multi_file(tmpdir) -> None:
    file2 = "test2.py"
    # language=python
    content2 = """
class A:
    pass
class B:
    pass
    """
    file = "test.py"
    # language=python
    content = """
from test2 import A
import test2

def foo(a: tuple[A, test2.B]) -> A:
    pass
class C(A):
    pass
class D(Generic[A]):
    pass
E: A = 1
F: int = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={file: content, file2: content2}) as codebase:
        a: PyFunction = codebase.get_symbol("A")
        b: PyFunction = codebase.get_symbol("B")
        c: PyClass = codebase.get_symbol("C")
        d: PyClass = codebase.get_symbol("D")
        e: PyAssignment = codebase.get_symbol("E")
        f: PyAssignment = codebase.get_symbol("F")
        foo: PyFunction = codebase.get_symbol("foo")
        annotation = foo.parameters[0].type
        assert foo.return_type.resolved_symbol == a
        assert foo.return_type == a
        assert annotation.parameters[0].resolved_symbol == a
        assert annotation.parameters[1].resolved_symbol == b
        assert annotation.parameters[0] == a
        assert annotation.parameters[1] == b
        assert c.is_subclass_of(a)
        assert not d.is_subclass_of(a)
        assert d.parent_classes[0].parameters[0] == a
        assert e.type.resolved_symbol == a
        assert e.type.resolved_symbol == a
        assert f.type.resolved_symbol is None
