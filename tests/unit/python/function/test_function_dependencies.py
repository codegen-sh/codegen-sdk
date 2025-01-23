from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_function_dependencies_symbol_usage(tmpdir) -> None:
    # language=python
    content = """
def a():
    pass

def b():
    pass

def c():
    return a() + b()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        c = file.get_function("c")
        assert len(c.dependencies) == 2
        assert set(c.dependencies) == {file.get_function("a"), file.get_function("b")}


def test_function_import_dependencies(tmpdir) -> None:
    # language=python
    content1 = """
from file2 import a, b

def c():
    return a() + b()
"""
    # language=python
    content2 = """
def a():
    pass

def b():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        c = file1.get_function("c")
        assert len(c.dependencies) == 2
        assert set(c.dependencies) == {file1.get_import("a"), file1.get_import("b")}


def test_function_import_dependencies_chained(tmpdir) -> None:
    # language=python
    content1 = """
import file2

def c():
    return file2.a() + file2.b()
"""
    # language=python
    content2 = """
def a():
    pass

def b():
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        c = file1.get_function("c")
        assert set(c.dependencies) == {file1.imports[0]}
        assert len(c.dependencies) == 1
