from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_set_comment(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        symbol.set_comment("this is a test comment")

    # Check that the comment was added
    assert "# this is a test comment\nsymbol = 1\n" in file.source


def test_set_comment_with_formatting(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        symbol.set_comment("# this is a test comment")

    # Check that the comment was added
    assert "# this is a test comment\nsymbol = 1\n" in file.source
    assert "##" not in file.source
    assert "# #" not in file.source


def test_set_comment_multiline(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        symbol.set_comment("this is a test comment\nthat spans multiple lines")

    # Check that the comment was added
    assert "# this is a test comment\n# that spans multiple lines\nsymbol = 1\n" in file.source


def test_set_comment_with_indentation(tmpdir) -> None:
    # language=python
    content = """
class MyClass:
    def foo(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        my_class = file.get_symbol("MyClass")
        foo = my_class.get_method("foo")
        foo.set_comment("this is a test comment")

    # Check that the comment was added
    assert "class MyClass:\n    # this is a test comment\n    def foo(self):\n        pass\n" in file.source


def test_add_comment(tmpdir) -> None:
    # language=python
    content = """
# this is an existing comment
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.add_comment("this is a test comment")

    # Check that the comment was added
    assert "# this is an existing comment\n# this is a test comment\nsymbol = 1\n" in file.source


def test_add_comment_new(tmpdir) -> None:
    # language=python
    content = """
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.add_comment("this is a test comment")

    # Check that the comment was added
    assert "# this is a test comment\nsymbol = 1\n" in file.source


def test_add_comment_with_formatting(tmpdir) -> None:
    # language=python
    content = """
# this is an existing comment
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.add_comment("# this is a test comment")

    # Check that the comment was added
    assert "# this is an existing comment\n# this is a test comment\nsymbol = 1\n" in file.source
    assert "##" not in file.source
    assert "# #" not in file.source


def test_add_comment_multiline(tmpdir) -> None:
    # language=python
    content = """
# this is an existing comment
# that spans multiple lines
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.add_comment("this is a test comment\nthat spans multiple lines")

    # Check that the comment was added
    assert "# this is an existing comment\n# that spans multiple lines\n# this is a test comment\n# that spans multiple lines\nsymbol = 1\n" in file.source


def test_add_comment_with_indentation(tmpdir) -> None:
    # language=python
    content = """
class MyClass:
    # this is an existing comment
    def foo(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        my_class = file.get_symbol("MyClass")
        foo = my_class.get_method("foo")
        foo.add_comment("this is a test comment")

    # Check that the comment was added
    assert "class MyClass:\n    # this is an existing comment\n    # this is a test comment\n    def foo(self):\n        pass\n" in file.source


def test_insert_comment(tmpdir) -> None:
    # language=python
    content = """
# this is a test comment
symbol = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment.source == "# this is a test comment"
        symbol.set_comment("this is an inserted comment")

    # Check that the comment was inserted
    assert "# this is an inserted comment\nsymbol = 1\n" in file.source


def test_insert_comment_multiline(tmpdir) -> None:
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
        symbol.set_comment("this is an inserted comment\nthat spans multiple lines")

    # Check that the comment was inserted
    assert "# this is an inserted comment\n# that spans multiple lines\nsymbol = 1\n" in file.source


def test_insert_comment_weird_spacing(tmpdir) -> None:
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
        symbol.set_comment("this is an inserted comment\n  that has weird spacing")

    # Check that the comment was inserted
    assert "# this is an inserted comment\n#   that has weird spacing\nsymbol = 1\n" in file.source


def test_insert_comment_with_indentation(tmpdir) -> None:
    # language=python
    content = """
class MyClass:
    # this is a test comment
    def foo(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        my_class = file.get_symbol("MyClass")
        foo = my_class.get_method("foo")
        assert foo.comment.source == "# this is a test comment"
        foo.set_comment("this is an inserted comment")

    # Check that the comment was inserted
    assert "class MyClass:\n    # this is an inserted comment\n    def foo(self):\n        pass\n" in file.source
