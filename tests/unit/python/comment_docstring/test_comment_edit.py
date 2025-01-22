from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_comment_edit_basic(tmpdir) -> None:
    # language=python
    content = """
# this is a test comment
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment"
        assert symbol.comment.text == "this is a test comment"
        symbol.comment.edit_text("this is an edited comment")

    # Check that the comment was edited
    assert "# this is an edited comment\n" in file.source


def test_comment_edit_source(tmpdir) -> None:
    # language=python
    content = """
# this is a test comment
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, verify_output=False) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment"
        assert symbol.comment.text == "this is a test comment"
        symbol.comment.edit("this is an edited comment")

    # Check that the comment was edited
    assert "this is an edited comment\n" in file.source
    assert "#" not in file.source


def test_comment_multiline(tmpdir) -> None:
    # language=python
    content = """
# this is a test comment
# that spans multiple lines
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment\n# that spans multiple lines"
        assert symbol.comment.text == "this is a test comment\nthat spans multiple lines"
        symbol.comment.edit_text("this is an edited comment\nthat spans multiple lines")

    # Check that the comment was edited
    assert "# this is an edited comment\n# that spans multiple lines\n" in file.source


def test_comment_weird_spacing(tmpdir) -> None:
    # language=python
    content = """
# this is a test comment
#that has weird spacing
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment\n#that has weird spacing"
        assert symbol.comment.text == "this is a test comment\nthat has weird spacing"
        symbol.comment.edit_text("this is an edited comment\nthat has weird spacing")

    # Check that the comment was edited
    assert "# this is an edited comment\n# that has weird spacing\n" in file.source


def test_comment_with_indentation_in_block(tmpdir) -> None:
    # language=python
    content = """
class A:
    # this is a test comment
    # that has indentation
    def symbol(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        A = file.get_symbol("A")
        symbol = A.get_method("symbol")
        assert symbol.comment.source == "# this is a test comment\n# that has indentation"
        assert symbol.comment.text == "this is a test comment\nthat has indentation"
        symbol.comment.edit_text("this is an edited comment\nthat has indentation")

    # Check that the comment was edited
    assert "    # this is an edited comment\n    # that has indentation\n" in file.source
