from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_no_docstring(tmpdir) -> None:
    # language=python
    content = """
def symbol():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is None


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
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is None
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a docstring\nthat has empty lines.\n\n\nAnd a second paragraph."
        assert symbol.docstring.source == '"""\n    This is a docstring\n    that has empty lines.\n\n\n    And a second paragraph.\n    """'


def test_docstring_with_comments(tmpdir) -> None:
    # language=python
    content = """
# This is a comment
def symbol():
    \"\"\"
    This is a docstring
    that has comments.
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        symbol = file.get_symbol("symbol")
        assert symbol.comment is not None
        assert symbol.comment.text == "This is a comment"
        assert symbol.docstring is not None
        assert symbol.docstring.text == "This is a docstring\nthat has comments."
        assert symbol.docstring.source == '"""\n    This is a docstring\n    that has comments.\n    """'


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

        func_b = class_a.get_method("funcB")
        assert func_b.comment is None
        assert func_b.docstring is not None
        assert func_b.docstring.text == "This is a docstring for function B."
        assert func_b.docstring.source == "'''\n        This is a docstring for function B.\n        '''"


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
