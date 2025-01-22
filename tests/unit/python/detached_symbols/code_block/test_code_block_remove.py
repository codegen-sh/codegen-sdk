from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_code_block_remove_multiple_element(tmpdir):
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    z = x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.statements[2].remove()
        code_block.statements.remove(code_block.statements[1])

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    """
    )


def test_code_block_remove_insert_beginning(tmpdir):
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    z = x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.statements[0].remove()
        code_block.statements.insert(0, "a = 3")

    # language=python
    assert (
        file.content
        == """
def foo():
    a = 3
    y = 2
    z = x + y
    """
    )


def test_code_block_insert_remove_beginning(tmpdir):
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    z = x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.statements.insert(0, "a = 3")
        code_block.statements[0].remove()

    # language=python
    assert (
        file.content
        == """
def foo():
    a = 3
    y = 2
    z = x + y
    """
    )


def test_code_block_remove_insert_middle(tmpdir):
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    z = x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.statements[1].remove()
        code_block.statements.append("a = 3")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    z = x + y
    a = 3
    """
    )


def test_code_block_insert_remove_middle(tmpdir):
    # language=python
    content = """
def foo():
    x = 1
    y = 2
    z = x + y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        code_block = file.get_function("foo").code_block
        code_block.statements.append("a = 3")
        code_block.statements[1].remove()

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    z = x + y
    a = 3
    """
    )
