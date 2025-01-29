from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.statements.statement import StatementType

if TYPE_CHECKING:
    from codegen.sdk.python import PyFile


def test_indent_left_once(tmpdir) -> None:
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    return x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(-1)

    # language=python
    assert (
        file.content
        == """
def foo():
x = 1
y = 2
return x + y
    """
    )


def test_indent_left_exceed_limit(tmpdir) -> None:
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    return x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(-5)

    # language=python
    assert (
        file.content
        == """
def foo():
x = 1
y = 2
return x + y
    """
    )


def test_indent_right_once(tmpdir) -> None:
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    return x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(1)

    # language=python
    assert (
        file.content
        == """
def foo():
        x = 1
        y = 2
        return x + y
    """
    )


def test_indent_right_multiple(tmpdir) -> None:
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    return x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(5)

    # language=python
    assert (
        file.content
        == """
def foo():
                        x = 1
                        y = 2
                        return x + y
    """
    )


def test_indent_zero(tmpdir) -> None:
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    return x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(0)
    assert file.content == content


def test_indent_nested_code_blocks(tmpdir) -> None:
    # language=python
    content = """
def foo():
    sum_val = 0
    is_threshold_reached = lambda: sum_val > threshold
    is_threshold_reached()

    for i in range(10):
        print(i)

    if a:
        if b:
            print(b)
        if c:
            print(c)
        elif d:
            return
    else:
        return

    if is_threshold_reached():
        return sum_val
    return 0
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.indent(-1)

    # language=python
    assert (
        file.content
        == """
def foo():
sum_val = 0
is_threshold_reached = lambda: sum_val > threshold
is_threshold_reached()

for i in range(10):
    print(i)

if a:
    if b:
        print(b)
    if c:
        print(c)
    elif d:
        return
else:
    return

if is_threshold_reached():
    return sum_val
return 0
    """
    )


def test_indent_only_nested_block(tmpdir) -> None:
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
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file: PyFile = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        if_block = code_block.if_blocks[0]
        if_block.consequence_block.indent(-1)
        nested_if = code_block.get_statements(StatementType.IF_BLOCK_STATEMENT)[1]
        nested_if.consequence_block.indent(1)

    # language=python
    assert (
        file.content
        == """
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
    )
