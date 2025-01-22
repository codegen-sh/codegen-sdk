import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.expressions import String


def test_string_edit(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
def foo():
    symbol = "test_string"
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        foo = codebase.get_symbol("foo")
        string = foo.code_block.statements[0].right
        assert isinstance(string, String)
        assert string == "test_string"
        string.content_nodes[0].edit("boop")
    # language=python
    assert (
        file.content
        == """
def foo():
    symbol = "boop"
"""
    )


def test_string_empty(tmpdir) -> None:
    # language=python
    content = """
def foo():
    symbol = ""
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        foo = codebase.get_symbol("foo")
        string = foo.code_block.statements[0].right
        assert isinstance(string, String)
        assert string == ""


def test_string_escape_sequence(tmpdir) -> None:
    # language=python
    content = """
escaped = "a\\a"
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        f = codebase.files[0]
        escaped = f.code_block.statements[0].right
        assert isinstance(escaped, String)
        assert escaped == "a\\a"


@pytest.mark.xfail(reason="Empty string edit not implemented")
def test_string_empty_edit(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
def foo():
    symbol = ""
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        foo = codebase.get_symbol("foo")
        string = foo.code_block.statements[0].right
        assert isinstance(string, String)
        assert string == ""
        string.content_nodes[0].edit("boop")
    # language=python
    assert (
        file.content
        == """
def foo():
    symbol = "boop"
"""
    )


def test_string_expressions(tmpdir) -> None:
    # language=python
    content = """
a = f"{foo(x, y)} + {bar()}"
    """
    with get_codebase_session(tmpdir, files={"test.py": content}) as codebase:
        f = codebase.get_file("test.py")
        a = f.get_global_var("a")
        assert isinstance(a.value, String)
        assert a.value == 'f"{foo(x, y)} + {bar()}"'
        assert len(a.value.expressions) == 2
        assert a.value.expressions[0] == "foo(x, y)"
        assert a.value.expressions[1] == "bar()"
