from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_set_docstring(tmpdir) -> None:
    # language=python
    content = """
def func():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring is None
        func.set_docstring("this is a docstring")

    # Check that the docstring was added
    assert 'def func():\n    """this is a docstring"""\n    pass\n' in file.source


def test_set_docstring_with_formatting(tmpdir) -> None:
    # language=python
    content = """
def func():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring is None
        func.set_docstring("\"\"\"this is a docstring'''")

    # Check that the docstring was added
    assert 'def func():\n    """this is a docstring"""\n    pass\n' in file.source
    assert "'''" not in file.source
    assert '""""""' not in file.source


def test_add_multiline_docstring(tmpdir) -> None:
    # language=python
    content = """
def func():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring is None
        func.set_docstring("this is a docstring\nthat spans multiple lines")

    # Check that the docstring was added
    assert 'def func():\n    """this is a docstring\n    that spans multiple lines\n    """\n    pass\n' in file.source


def test_set_docstring_with_indentation(tmpdir) -> None:
    # language=python
    content = """
def func():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring is None
        func.set_docstring("this is a docstring\n    with indentation")

    # Check that the docstring was added
    assert 'def func():\n    """this is a docstring\n        with indentation\n    """\n    pass\n' in file.source


def test_set_docstring_empty_lines(tmpdir) -> None:
    # language=python
    content = """
def func():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring is None
        func.set_docstring("this is a docstring\n\n\nwith empty lines")

    # Check that the docstring was added
    # language=python
    assert (
        file.content
        == '''
def func():
    """this is a docstring


    with empty lines
    """
    pass
'''
    )


def test_set_docstring_in_class(tmpdir) -> None:
    # language=python
    content = """
class MyClass:
    def foo(self):
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        my_class = file.get_symbol("MyClass")
        my_class.set_docstring("this is a class docstring")
        foo = my_class.get_method("foo")
        assert foo.docstring is None
        foo.set_docstring("this is a function docstring.\nthese are multiple lines.")

    # Check that the docstring was added
    assert (
        'class MyClass:\n    """this is a class docstring"""\n    def foo(self):\n        """this is a function docstring.\n        these are multiple lines.\n        """\n        pass\n'
        in file.source
    )


def test_insert_docstring(tmpdir) -> None:
    # language=python
    content = """
def func():
    \"\"\"this is a docstring\"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        func = file.get_symbol("func")
        assert func.docstring.source == '"""this is a docstring"""'
        assert func.docstring.text == "this is a docstring"
        func.set_docstring("this is an inserted docstring")

    # Check that the docstring was inserted
    assert 'def func():\n    """this is an inserted docstring"""\n    pass\n' in file.source
