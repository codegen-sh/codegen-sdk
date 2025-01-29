from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.statements.statement import StatementType

if TYPE_CHECKING:
    from codegen.sdk.python import PyFile


def test_unwrap_flat_statements(tmpdir):
    # language=python
    content = """
def foo():
    if a:
        print(a)
    elif b:
        print(b)
    else:
        print(c)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        function.code_block.unwrap()
    # language=python
    assert (
        file.content
        == """
if a:
    print(a)
elif b:
    print(b)
else:
    print(c)
    """
    )


def test_unwrap_nested_statements(tmpdir):
    # language=python
    content = """
def foo():
    if a:
        if b:
            print(b)
        if c:
            print(c)
        elif d:
            return
    else:
        return
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        nested_if = function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT)[1]
        nested_if.consequence_block.unwrap()
    # language=python
    assert (
        file.content
        == """
def foo():
    if a:
        print(b)
        if c:
            print(c)
        elif d:
            return
    else:
        return
    """
    )


def test_unwrap_sandwiched_statements(tmpdir):
    # language=python
    content = """
def foo():
    if a:
        print(a)
    elif b:
        print(b)
        print(b + c)
    elif c:
        print(c)
    else:
        print(d)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}, verify_output=False, sync_graph=False) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        if_block = function.code_block.if_blocks[0]
        if_block.elif_statements[0].consequence_block.unwrap()
    # language=python
    assert (
        file.content
        == """
def foo():
    if a:
        print(a)
    print(b)
    print(b + c)
    elif c:
        print(c)
    else:
        print(d)
    """
    )


def test_unwrap_multiline_wrapper(tmpdir):
    # language=python
    content = """
def foo():
    if (
        condition1 and
        condition2 and
        (condition3 or condition4)
    ):
        # if comment
        print(a)
        print(b)
        # middle if comment
        if (a):
            # nested comment
            print(a)

    i = 0
    while (
        i < len(array) and
        array[i] is not None and
        (array[i].is_valid() or array[i].can_be_processed())
    ):
        # Loop body 1
        print(array[i])
        i += 1

    while (
        condition1 and
        condition2 and
        (condition3 or condition4) and
        some_function()
    ):
        # Loop body 2
        # Code to execute while the conditions are true
        pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        block_statements = function.code_block.get_statements(max_level=function.code_block.level)
        for block_statement in block_statements:
            for code_block in block_statement.nested_code_blocks:
                code_block.unwrap()
    # language=python
    assert (
        file.content
        == """
def foo():
    # if comment
    print(a)
    print(b)
    # middle if comment
    if (a):
        # nested comment
        print(a)

    i = 0
    # Loop body 1
    print(array[i])
    i += 1

    # Loop body 2
    # Code to execute while the conditions are true
    pass
    """
    )
