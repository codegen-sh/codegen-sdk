from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_oneline_docstring(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"This is a one-line docstring.\"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a one-line docstring."
        assert symbol.docstring.source == '"""This is a one-line docstring."""'
        symbol.docstring.edit_text("This is an edited one-line docstring.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """This is an edited one-line docstring."""\n    pass\n' in file.source


def test_docstring_source(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"This is a one-line docstring.\"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, verify_output=False) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a one-line docstring."
        assert symbol.docstring.source == '"""This is a one-line docstring."""'
        symbol.docstring.edit("This is a new docstring.")

    # Check that the docstring was edited
    assert "def symbol():\n    This is a new docstring.\n    pass\n" in file.source


def test_docstring_single_quote(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    '''This is a one-line docstring.'''
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a one-line docstring."
        assert symbol.docstring.source == "'''This is a one-line docstring.'''"
        symbol.docstring.edit_text("This is an edited one-line docstring.")

    # Check that the docstring was edited
    assert "def symbol():\n    '''This is an edited one-line docstring.'''\n    pass\n" in file.source


def test_docstring_single_to_multiline(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"This is a one-line docstring.\"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.docstring.edit_text("This is an edited multi-line docstring.\nIt has multiple lines.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """This is an edited multi-line docstring.\n    It has multiple lines.\n    """\n    pass\n' in file.source


def test_docstring_multiline_to_single(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
    This is a multi-line docstring.
    It has multiple lines.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        symbol.docstring.edit_text("This is an edited one-line docstring.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """This is an edited one-line docstring."""\n    pass\n' in file.source


def test_multiline_docstring(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
    This is a multi-line docstring.
    It has multiple lines.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a multi-line docstring.\nIt has multiple lines."
        assert symbol.docstring.source == '"""\n    This is a multi-line docstring.\n    It has multiple lines.\n    """'
        symbol.docstring.edit_text("This is an edited multi-line docstring.\nIt has multiple lines.")


def test_multiline_docstring_google_style(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"This is a multi-line docstring.
    It has multiple lines.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a multi-line docstring.\nIt has multiple lines."
        assert symbol.docstring.source == '"""This is a multi-line docstring.\n    It has multiple lines.\n    """'
        symbol.docstring.edit_text("This is an edited multi-line docstring.\nIt has multiple lines.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """This is an edited multi-line docstring.\n    It has multiple lines.\n    """\n    pass\n' in file.source


def test_docstring_with_indentation(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
        This is a docstring
        that has indentation.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a docstring\nthat has indentation."
        assert symbol.docstring.source == '"""\n        This is a docstring\n        that has indentation.\n    """'
        symbol.docstring.edit_text("    This is an edited docstring\n    that has indentation.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """\n        This is an edited docstring\n        that has indentation.\n    """\n    pass\n' in file.source


def test_docstring_partial_indentation(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
        This is a docstring
    that has partial indentation.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "    This is a docstring\nthat has partial indentation."
        assert symbol.docstring.source == '"""\n        This is a docstring\n    that has partial indentation.\n    """'
        symbol.docstring.edit_text("    This is an edited docstring\nthat has partial indentation.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """\n        This is an edited docstring\n    that has partial indentation.\n    """\n    pass\n' in file.source


def test_docstring_empty_lines(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
    This is a docstring
    that has empty lines.


    And a second paragraph.
    \"\"\"
    pass
"""
    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert (
            symbol.docstring.text
            == """This is a docstring
that has empty lines.


And a second paragraph."""
        )
        assert symbol.docstring.source == '"""\n    This is a docstring\n    that has empty lines.\n\n\n    And a second paragraph.\n    """'
        new_docstring = """This is an edited docstring
that has empty lines.


And an edited second paragraph."""
        symbol.docstring.edit_text(new_docstring)

    # Check that the docstring was edited
    # language=python
    assert (
        file.content
        == '''
def symbol():
    """
    This is an edited docstring
    that has empty lines.


    And an edited second paragraph.
    """
    pass
'''
    )


def test_docstring_weird_spacing(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    \"\"\"
    This is a docstring
    with weird spacing.\"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a docstring\nwith weird spacing."
        assert symbol.docstring.source == '"""\n    This is a docstring\n    with weird spacing."""'
        symbol.docstring.edit_text("This is an edited docstring\nwith no more weird spacing.")

    # Check that the docstring was edited
    assert 'def symbol():\n    """\n    This is an edited docstring\n    with no more weird spacing.\n    """\n    pass\n' in file.source


def test_docstring_classes(tmpdir) -> None:
    # language=python
    content = """
class SymbolA:
    \"\"\"
    This is a docstring for class A.
    \"\"\"

    def funcB(self):
        '''
        This is a docstring for function B.
        '''
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_a = file.get_symbol("SymbolA")
        assert class_a.comment is None
        assert class_a.docstring is not None
        assert class_a.docstring.text == "This is a docstring for class A."
        assert class_a.docstring.source == '"""\n    This is a docstring for class A.\n    """'
        class_a.docstring.edit_text("This is an edited docstring for class A.")

        func_b = class_a.get_method("funcB")
        assert func_b.comment is None
        assert func_b.docstring is not None
        assert func_b.docstring.text == "This is a docstring for function B."
        assert func_b.docstring.source == "'''\n        This is a docstring for function B.\n        '''"
        func_b.docstring.edit_text("This is an edited docstring for function B.")

    # Check that the docstrings were edited
    assert 'class SymbolA:\n    """This is an edited docstring for class A."""' in file.source
    assert "    def funcB(self):\n        '''This is an edited docstring for function B.'''" in file.source


def test_docstring_classes_google_style(tmpdir) -> None:
    # language=python
    content = """
class SymbolA:
    def funcB(self):
        '''This is a docstring for function B.
        that is in Google style.
        '''
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_a = file.get_symbol("SymbolA")
        func_b = class_a.get_method("funcB")
        assert func_b.comment is None
        assert func_b.docstring is not None
        assert func_b.docstring.text == "This is a docstring for function B.\nthat is in Google style."
        assert func_b.docstring.source == "'''This is a docstring for function B.\n        that is in Google style.\n        '''"
        func_b.docstring.edit_text("This is an edited docstring for function B.\nthat is in Google style.")

    # Check that the docstring was edited
    assert "class SymbolA:\n    def funcB(self):\n        '''This is an edited docstring for function B.\n        that is in Google style.\n        '''" in file.source
