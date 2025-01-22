from codegen_sdk.codebase.factory.get_session import get_codebase_session


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
