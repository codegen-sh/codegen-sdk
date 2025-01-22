from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_comment_inline(tmpdir) -> None:
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
        symbol.inline_comment.edit_text("this is an edited inline comment")

    # Check that the comment was edited
    assert "symbol = 1  # this is an edited inline comment\n" in file.source


def test_comment_inline_source(tmpdir) -> None:
    # language=python
    content = """
symbol = 1  # this is an inline comment
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, verify_output=False) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.inline_comment.source == "# this is an inline comment"
        assert symbol.inline_comment.text == "this is an inline comment"
        symbol.inline_comment.edit("this is an edited inline comment")

    # Check that the comment was edited
    assert "symbol = 1  this is an edited inline comment\n" in file.source
