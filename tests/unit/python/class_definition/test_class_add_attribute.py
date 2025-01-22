from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_class_definition_add_attribute_adds_source(tmpdir) -> None:
    # language=python
    content = """
class Foo:
    def foo(fun):
        return fun

class Bar:
    bar: int = 0
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        foo_class = file.get_class("Foo")
        bar_class = file.get_class("Bar")
        foo_class.add_attribute(bar_class.get_attribute("bar"))
    # language=python
    assert (
        file.content
        == """
class Foo:
    bar: int = 0

    def foo(fun):
        return fun

class Bar:
    bar: int = 0
"""
    )


def test_class_definition_add_attribute_include_deps(tmpdir) -> None:
    # language=python
    src_content = """
from typing import List

class Bar:
    bar: List[int] = []
"""
    # language=python
    dest_content = """
class Foo:
    def foo(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"src.py": src_content, "dest.py": dest_content}) as codebase:
        src_file = codebase.get_file("src.py")
        dest_file = codebase.get_file("dest.py")

        foo_class = dest_file.get_class("Foo")
        bar_class = src_file.get_class("Bar")
        foo_class.add_attribute(bar_class.get_attribute("bar"), include_dependencies=True)

    # language=python
    assert (
        dest_file.content
        == """from typing import List

class Foo:
    bar: List[int] = []

    def foo(fun):
        return fun
"""
    )


def test_class_definition_add_attribute_from_source(tmpdir) -> None:
    # language=python
    src_content = """
class A:
    a: int
    b: int

class B:
    pass

class C:
    '''docstring'''
    def f(self) -> None:
        pass
"""

    with get_codebase_session(tmpdir=tmpdir, files={"src.py": src_content}) as codebase:
        src_file = codebase.get_file("src.py")

        # =====[ A ]=====
        A = src_file.get_class("A")
        A.add_attribute_from_source("c: int")

        # =====[ B ]=====
        B = src_file.get_class("B")
        B.add_attribute_from_source("c: int")

        # =====[ C ]=====
        C = src_file.get_class("C")
        C.add_attribute_from_source("c: int")

    # language=python
    assert (
        src_file.content
        == """
class A:
    a: int
    b: int
    c: int

class B:
    c: int
    pass

class C:
    '''docstring'''
    c: int

    def f(self) -> None:
        pass
"""
    )
