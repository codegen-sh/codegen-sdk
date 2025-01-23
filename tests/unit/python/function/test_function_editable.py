from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_extended_function_source(tmpdir) -> None:
    # language=python
    content = """
@decorator
# comment
def foo(arg1, arg2):
    \"\"\"docstring\"\"\"
    pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        foo = file.get_symbol("foo")
        assert (
            foo.source
            == """
@decorator
# comment
def foo(arg1, arg2):
    \"\"\"docstring\"\"\"
    pass
""".strip()
        )


def test_extended_function_edit(tmpdir) -> None:
    # language=python
    content = """
@decorator
# comment
def foo(arg1, arg2):
    \"\"\"docstring\"\"\"
    pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        foo = file.get_symbol("foo")
        foo.edit(
            """
@test
# another comment
def bar():
    \"\"\"yolo\"\"\"
    pass
""".strip()
        )

    # language=python
    assert (
        file.source
        == """
@test
# another comment
def bar():
    \"\"\"yolo\"\"\"
    pass
""".lstrip()  # lstrip to keep trailing newline
    )


def test_extended_function_edit_equals(tmpdir) -> None:
    # language=python
    content = """
@decorator
# comment
def foo(arg1, arg2):
    \"\"\"docstring\"\"\"
    pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        foo = file.get_symbol("foo")
        foo.source = """
@test
# another comment
def bar():
    \"\"\"yolo\"\"\"
    pass
""".strip()

    # language=python
    assert (
        file.source
        == """
@test
# another comment
def bar():
    \"\"\"yolo\"\"\"
    pass
""".lstrip()  # lstrip to keep trailing newline
    )
