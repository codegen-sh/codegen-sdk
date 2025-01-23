from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_global_vars(tmpdir) -> None:
    # language=python
    content = """
# comment

'''
multi-line-comment
'''

var = 5
other_var: int = 10
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert file.symbols == file.global_vars
        symbols = file.global_vars
        assert len(symbols) == 2
        assert set([x.name for x in symbols]) == {"var", "other_var"}


def test_global_var_only_counts_left_side(tmpdir) -> None:
    # language=python
    content = """
a = 1
b = a
b = c
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        assert file.symbols == file.global_vars
        symbols = file.global_vars
        assert len(symbols) == 3
        assert set([x.name for x in symbols]) == {"a", "b"}


def test_global_var_comments_not_included(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# DO NOT INCLUDE

foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_global_var("foo")

        assert foo.comment is None
        assert foo.inline_comment is None
        assert "DO NOT INCLUDE" not in foo.extended_source
        assert "DO NOT INCLUDE" not in foo.source
        assert "foo = 1" in foo.source
        assert "foo = 1" in foo.extended_source


def test_global_var_comment_included(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is a comment
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_global_var("foo")

        assert foo.comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "foo = 1" in foo.source
        assert "foo = 1" in foo.extended_source


def test_global_var_broken_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# DO NOT INCLUDE
# DO NOT INCLUDE

# This is comment 1
# This is comment 2
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_global_var("foo")

        assert foo.comment.source == "# This is comment 1\n# This is comment 2"
        assert "# This is comment 1" in foo.extended_source
        assert "# This is comment 2" in foo.extended_source
        # assert "# This is comment 1" not in foo.source
        # assert "# This is comment 2" not in foo.source
        assert "DO NOT INCLUDE" not in foo.extended_source
        assert "DO NOT INCLUDE" not in foo.source
        assert "foo = 1" in foo.source
        assert "foo = 1" in foo.extended_source


def test_global_var_multiline_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is comment 1
# This is comment 2
# This is comment 3
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_global_var("foo")

        assert foo.comment.source == "# This is comment 1\n# This is comment 2\n# This is comment 3"
        assert "# This is comment 1" in foo.extended_source
        assert "# This is comment 2" in foo.extended_source
        assert "# This is comment 3" in foo.extended_source
        # assert "# This is comment 1" not in foo.source
        # assert "# This is comment 2" not in foo.source
        # assert "# This is comment 3" not in foo.source
        assert "foo = 1" in foo.source
        assert "foo = 1" in foo.extended_source


def test_global_var_inline_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
foo = 1  # This is a comment
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_global_var("foo")

        assert foo.comment is None
        assert foo.inline_comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "foo = 1" in foo.source
        assert "foo = 1" in foo.extended_source
