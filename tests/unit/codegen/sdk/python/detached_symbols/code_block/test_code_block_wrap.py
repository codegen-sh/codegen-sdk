from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session

if TYPE_CHECKING:
    from codegen.sdk.python import PyFile


def test_wrap_with_with_statement(tmpdir):
    # language=python
    content = """
def foo(a: bool):
    if a:
        print(a)
    else:
        print(b)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        function.code_block.wrap(before_src="with open('test.txt', 'w') as f:")
    # language=python
    assert (
        file.content
        == """
def foo(a: bool):
    with open('test.txt', 'w') as f:
        if a:
            print(a)
        else:
            print(b)
    """
    )


def test_wrap_with_function(tmpdir):
    # language=python
    content = """
if a:
    print(a)
else:
    print(b)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        file.code_block.wrap("def func(a, b):")
    # language=python
    assert (
        file.content
        == """
def func(a, b):
    if a:
        print(a)
    else:
        print(b)
    """
    )
