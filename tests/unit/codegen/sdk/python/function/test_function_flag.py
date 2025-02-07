from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage


def test_function_flag_with_pointer(tmpdir):
    # language=python
    content = """
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, programming_language=ProgrammingLanguage.PYTHON) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        foo.flag(message="This is a test")
        codebase.commit()

        expected = """
def foo():
    pass  # 👈 🚩 This is a test
"""
        assert file.content == expected


def test_function_flag_without_message(tmpdir):
    # language=python
    content = """
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, programming_language=ProgrammingLanguage.PYTHON) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        foo.flag()
        codebase.commit()

        expected = """
def foo():
    pass  # 👈 🚩
"""
        assert file.content == expected
