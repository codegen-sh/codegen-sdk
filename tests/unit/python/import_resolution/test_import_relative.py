from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_import_relative(tmpdir) -> None:
    # language=python
    content1 = """
from .file2 import foo
foo()
"""
    # language=python
    content2 = """
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        foo_call = file1.function_calls[0]
        foo = file2.get_function("foo")
        assert set(foo.call_sites) == {foo_call}


def test_import_relative_up(tmpdir) -> None:
    # language=python
    content1 = """
from ..file2 import foo
foo()
"""
    # language=python
    content2 = """
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/subdir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/subdir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        foo_call = file1.function_calls[0]
        foo = file2.get_function("foo")
        assert set(foo.call_sites) == {foo_call}


def test_import_relative_multi_up(tmpdir) -> None:
    # language=python
    content1 = """
from ...file2 import foo
foo()
"""
    # language=python
    content2 = """
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/subdir/file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/subdir/file1.py")
        file2 = codebase.get_file("file2.py")
        foo_call = file1.function_calls[0]
        foo = file2.get_function("foo")
        assert set(foo.call_sites) == {foo_call}
