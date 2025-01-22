import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_function_insert_statements_add_source(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo_function = file.get_function("foo")
        foo_function.insert_statements("print('hello world')")

    assert "print('hello world')" in file.content


def test_function_insert_statements_index_out_of_range_raises(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo_function = file.get_function("foo")
        with pytest.raises(ValueError):
            foo_function.insert_statements("print('hello world')", index=100)
