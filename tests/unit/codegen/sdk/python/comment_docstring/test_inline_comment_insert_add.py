from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_set_comment_inline(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.inline_comment is None
        symbol.set_inline_comment("this is an inline comment")

    # Check that the comment was added
    assert "symbol = 1  # this is an inline comment\n" in file.source


def test_set_comment_inline_with_formatting(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.inline_comment is None
        symbol.set_inline_comment("# this is an inline comment")

    # Check that the comment was added
    assert "symbol = 1  # this is an inline comment\n" in file.source
    assert "##" not in file.source
    assert "# #" not in file.source


def test_insert_comment_inline(tmpdir) -> None:
    # language=python
    content = """
symbol = 1  # this is an inline comment
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.inline_comment.source == "# this is an inline comment"
        assert symbol.inline_comment.text == "this is an inline comment"
        symbol.set_inline_comment("this is an inserted inline comment")

    # Check that the comment was inserted
    assert "symbol = 1  # this is an inserted inline comment" in file.source
