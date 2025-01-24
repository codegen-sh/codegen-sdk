from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.external_module import ExternalModule


def test_import_resolved_symbol(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    pass
    """
    # language=python
    content2 = """
from file1 import foo

def bar():
    foo()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")

        foo = file1.get_function("foo")
        assert file2.get_import("foo").resolved_symbol == foo


def test_import_resolved_symbol_external_module(tmpdir) -> None:
    # language=python
    content = """
import numpy as np

def foo():
    return np.array()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content}) as codebase:
        file1 = codebase.get_file("file1.py")

        np = file1.get_import("np")
        assert isinstance(np.resolved_symbol, ExternalModule)
        assert np.resolved_symbol.name == "numpy"


def test_import_resolved_symbol_file(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    pass
    """
    # language=python
    content2 = """
from dir import file1

def bar():
    file1.foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        assert file2.get_import("file1").resolved_symbol == file1


def test_import_resolved_symbol_multi_hop(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    pass
    """
    # language=python
    content2 = """
from file1 import foo

def bar():
    foo()
    """
    # language=python
    content3 = """
from file2 import foo

def baz():
    foo()
    """
    # language=python
    content4 = """
from file3 import foo

def qux():
    foo()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, "file3.py": content3, "file4.py": content4}) as codebase:
        file1 = codebase.get_file("file1.py")
        file4 = codebase.get_file("file4.py")

        foo = file1.get_function("foo")
        assert file4.get_import("foo").resolved_symbol == foo


def test_import_resolved_symbol_import_loop(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    pass
    """
    # language=python
    content2 = """
from file4 import foo

def bar():
    foo()
    """
    # language=python
    content3 = """
from file2 import foo

def baz():
    foo()
    """
    # language=python
    content4 = """
from file3 import foo

def qux():
    foo()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, "file3.py": content3, "file4.py": content4}) as codebase:
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")
        file4 = codebase.get_file("file4.py")

        assert file2.get_import("foo").resolved_symbol == file4.get_import("foo")
        assert file3.get_import("foo").resolved_symbol == file2.get_import("foo")
        assert file4.get_import("foo").resolved_symbol == file3.get_import("foo")
