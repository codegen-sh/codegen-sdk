from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_comment_basic(tmpdir) -> None:
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


def test_comment_no_comment(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None


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


def test_comment_with_indentation(tmpdir) -> None:
    # language=python
    content = """
    # this is a test comment
    # that has indentation
    symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment\n# that has indentation"
        assert symbol.comment.text == "this is a test comment\nthat has indentation"


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


def test_comment_with_spacing(tmpdir) -> None:
    # language=python
    content = """
#       this is a test comment
#     that has spacing
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "#       this is a test comment\n#     that has spacing"
        assert symbol.comment.text == "      this is a test comment\n    that has spacing"
