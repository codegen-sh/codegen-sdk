from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.import_resolution import Import


def test_function_symbol_dependencies(tmpdir) -> None:
    # language=python
    content = """
from file2 import x, y, z

GLOBAL_VAR_1 = 234
GLOBAL_VAR_2 = 432

def foo():
    return bar() + GLOBAL_VAR_1

def bar():
    return 42

class MyClass:
    def __init__(self):
        pass

    def method1(self):
        return foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        symbols = file.symbols
        assert len(symbols) == 5
        assert set(s.name for s in symbols) == {"GLOBAL_VAR_1", "GLOBAL_VAR_2", "foo", "bar", "MyClass"}

        foo_deps = file.get_symbol("foo").dependencies
        assert set(d.name for d in foo_deps) == {"bar", "GLOBAL_VAR_1"}

        bar_deps = file.get_symbol("bar").dependencies
        assert set(d.name for d in bar_deps) == set()

        method1_deps = file.get_class("MyClass").get_method("method1").dependencies
        assert set(d.name for d in method1_deps) == {"foo"}


def test_function_import_dependencies(tmpdir) -> None:
    # language=python
    content = """
from a.b import (c as d, e as f)
from type_package import ParameterType, ReturnType

def g(tmpdir):
    f()

@d.test("abc")
def h(tmpdir):
    g()

@f.test("abc")
def i(x: ParameterType) -> ReturnType:
    g()

"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # =====[ Easier case ]=====
        func = file.get_function("h")
        deps = func.dependencies
        assert len(deps) == 2
        assert "g" in [d.name for d in deps]
        assert "d" in [d.name for d in deps]

        # =====[ Harder case ]=====
        symbol = file.get_function("i")
        deps = symbol.dependencies
        assert len(deps) == 4
        assert "g" in [d.name for d in deps]
        assert "ParameterType" in [d.name for d in deps]
        assert "ReturnType" in [d.name for d in deps]
        assert "f" in [d.name for d in deps]


def test_decorated_function_dependencies(tmpdir) -> None:
    # language=python
    content = """
from d.e.f import MyType
from a.b.c import my_decorator
from g.h.i import my_module

@my_decorator
@my_module.decorate_func("test")
def f(tmpdir):
    return MyType()

@my_module.decorate_attr
def g(tmpdir):
    return MyType()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        f_deps = file.get_symbol("f").dependencies
        assert any((isinstance(dep, Import) and dep.alias.source == "MyType") for dep in f_deps)
        assert any((isinstance(dep, Import) and dep.alias.source == "my_decorator") for dep in f_deps)
        assert any((isinstance(dep, Import) and dep.alias.source == "my_module") for dep in f_deps)

        g_deps = file.get_symbol("g").dependencies
        assert any((isinstance(dep, Import) and dep.alias.source == "MyType") for dep in g_deps)
        assert any((isinstance(dep, Import) and dep.alias.source == "my_module") for dep in g_deps)


def test_function_parameter_dependencies(tmpdir) -> None:
    # language=python
    content = """
from a import B
from typing import Optional

def g() -> B:  # easy
    return None

def f() -> B | None:
    return None

def h() -> Optional[B]:
    pass

def i() -> Optional[B] | None:
    pass

def k() -> Optional[B] | None | B:
    pass

"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        assert set(dep.name for dep in file.get_symbol("f").dependencies) == {"B"}
        assert set(dep.name for dep in file.get_symbol("g").dependencies) == {"B"}
        assert set(dep.name for dep in file.get_symbol("h").dependencies) == {"B", "Optional"}
        assert set(dep.name for dep in file.get_symbol("i").dependencies) == {"B", "Optional"}
        assert set(dep.name for dep in file.get_symbol("k").dependencies) == {"B", "Optional"}
