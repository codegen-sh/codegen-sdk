from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_code_block_append_single_element(tmpdir):
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

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    z = x + y
    a = 3
    """
    )


def test_code_block_append_multiple_element(tmpdir):
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
        code_block.statements.append("b = 4")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    z = x + y
    a = 3
    b = 4
    """
    )


def test_code_block_insert_single_element_beginning(tmpdir):
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

    # language=python
    assert (
        file.content
        == """
def foo():
    a = 3
    x = 1
    y = 2
    z = x + y
    """
    )


def test_code_block_insert_multiple_element_beginning(tmpdir):
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
        code_block.statements.insert(0, "b = 4")

    # language=python
    assert (
        file.content
        == """
def foo():
    b = 4
    a = 3
    x = 1
    y = 2
    z = x + y
    """
    )


def test_code_block_insert_single_element_middle(tmpdir):
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
        code_block.statements.insert(2, "a = 3")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    a = 3
    z = x + y
    """
    )


def test_code_block_insert_multiple_element_middle(tmpdir):
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
        code_block.statements.insert(2, "a = 3")
        code_block.statements.insert(2, "b = 4")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    b = 4
    a = 3
    z = x + y
    """
    )


def test_code_block_insert_single_element_end(tmpdir):
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
        code_block.statements.insert(3, "a = 3")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    z = x + y
    a = 3
    """
    )


def test_code_block_insert_multiple_element_end(tmpdir):
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
        code_block.statements.insert(3, "a = 3")
        code_block.statements.insert(3, "b = 4")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    y = 2
    z = x + y
    b = 4
    a = 3
    """
    )


def test_code_block_insert_multiple_out_of_order(tmpdir):
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
        code_block.statements.insert(3, "c = 5")
        code_block.statements.insert(1, "a = 3")
        code_block.statements.insert(2, "b = 4")

    # language=python
    assert (
        file.content
        == """
def foo():
    x = 1
    a = 3
    b = 4
    y = 2
    z = x + y
    c = 5
    """
    )
