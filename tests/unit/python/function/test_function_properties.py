from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_functions(tmpdir) -> None:
    # language=python
    content = """
def f(tmpdir):
    pass

def g(x: int):
    pass

def h(x: int) -> str:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # ======[ Grab the nodes ]=====
        assert file.symbols == file.functions
        symbols = file.functions
        names = [x.name for x in symbols]
        assert "f" in names
        assert "g" in names
        assert "h" in names


def test_function_return_type_annotation(tmpdir) -> None:
    # language=python
    content = """
def f() -> Tuple[a, b, c]:
    return
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        symbols = file.symbols
        assert len(symbols) == 1
        symbol = file.get_function("f")
        assert symbol.return_type.source == "Tuple[a, b, c]"


def test_decorated_function(tmpdir) -> None:
    # language=python
    content = """
@decorator
def my_func(tmpdir):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        function_symbol = file.get_function("my_func")
        assert function_symbol.name == "my_func"
        assert "@decorator" in function_symbol.source


def test_function_decorators(tmpdir) -> None:
    # language=python
    content = """
@thing1
@thing2(1, '2', a=3)
@thing3.abc
@thing4.xyz(1, '2', a=3)
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        function_symbol = file.get_function("foo")
        assert len(function_symbol.decorators) == 4

        # thing1
        assert function_symbol.decorators[0].source == "@thing1"
        assert function_symbol.decorators[0].name == "thing1"

        # thing2
        assert function_symbol.decorators[1].source == "@thing2(1, '2', a=3)"
        assert function_symbol.decorators[1].name == "thing2"
        # TODO: Test arguments

        # thing3
        assert function_symbol.decorators[2].source == "@thing3.abc"
        assert function_symbol.decorators[2].full_name == "thing3.abc"

        # thing4
        assert function_symbol.decorators[3].source == "@thing4.xyz(1, '2', a=3)"
        assert function_symbol.decorators[3].full_name == "thing4.xyz"
        # TODO: Test arguments


def test_function_definition_docstring(tmpdir) -> None:
    # Test Python file
    # language=python
    python_code = """
def foo(bar: int) -> None:
    return None

def bar():
    return 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": python_code}) as codebase:
        file = codebase.get_file("test.py")
        foo_func = file.get_function("foo")
        assert foo_func.function_signature == "def foo(bar: int) -> None:"

        bar_func = file.get_function("bar")
        assert bar_func.function_signature == "def bar():"


def test_function_docstring(tmpdir) -> None:
    # language=python
    content = """
def foo():
    \"\"\"This is a docstring\"\"\"
    pass

def bar():
    \"\"\"
    This is a multiline docstring
    @param
    @return
    \"\"\"
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        function_symbol = file.get_function("foo")
        assert function_symbol.docstring.text == "This is a docstring"
        assert "foo" not in function_symbol.docstring.text
        assert "pass" not in function_symbol.docstring.text

        function_symbol = codebase.get_symbol("bar")
        assert "This is a multiline docstring" in function_symbol.docstring.text
        assert "@param" in function_symbol.docstring.text
        assert "@return" in function_symbol.docstring.text
        assert "bar" not in function_symbol.docstring.text
        assert "pass" not in function_symbol.docstring.text


def test_function_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is a comment
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_function("foo")

        assert foo.comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "def foo():" in foo.source
        assert "def foo():" in foo.extended_source


def test_decorated_function_comment(tmpdir) -> None:
    FILENAME = "test_file.py"
    # language=python
    FILE_CONTENT = """
# This is a comment
@decorator
def foo():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: FILE_CONTENT.strip()}) as codebase:
        file = codebase.get_file(FILENAME)
        foo = file.get_function("foo")

        assert foo.comment.source == "# This is a comment"
        assert "# This is a comment" in foo.extended_source
        # assert "# This is a comment" not in foo.source
        assert "@decorator" in foo.extended_source
        # assert "@decorator" not in foo.source
        assert "def foo():" in foo.source
        assert "def foo():" in foo.extended_source


def test_function_level(tmpdir) -> None:
    # language=python
    content = """
def f():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        # Test top-level function
        function_f = file.get_function("f")
        assert function_f.code_block.level == 1


def test_function_return_statements(tmpdir) -> None:
    # language=python
    content = """
def foo(a):
    if a == 1:
        return True
    else:
        return False
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        function_symbol = file.get_function("foo")
        assert len(function_symbol.return_statements) == 2
        assert function_symbol.return_statements[0].source == "return True"
        assert function_symbol.return_statements[0].value == "True"
        assert function_symbol.return_statements[1].source == "return False"
        assert function_symbol.return_statements[1].value == "False"


def test_method_return_statements(tmpdir) -> None:
    # language=python
    content = """
class A:
    def f(self) -> int:
        return 5 + 5

    def g(self):
        return

    def h(self) -> str:
        if True:
            return "hello"
        else:
            return "world"
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        cls = file.get_class("A")

        # =====[ f ]=====
        f = cls.get_method("f")
        return_statements = f.return_statements
        assert len(return_statements) == 1
        assert return_statements[0].value == "5 + 5"

        # =====[ g ]=====
        g = cls.get_method("g")
        return_statements = g.return_statements
        assert len(return_statements) == 1
        assert return_statements[0].value is None

        # =====[ h ]=====
        h = cls.get_method("h")
        return_statements = h.return_statements
        assert len(return_statements) == 2
        assert return_statements[0].value == '"hello"'
        assert return_statements[1].value == '"world"'


def test_function_parameters(tmpdir) -> None:
    # language=python
    content = """
from a.b import MyType

def f(a, b: int, c: str = "hello", d: MyType = None) -> MyType:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        func = file.get_function("f")
        params = func.parameters
        assert len(params) == 4
        assert "a" in [x.name for x in params]
        assert "b" in [x.name for x in params]
        assert "c" in [x.name for x in params]
        assert "d" in [x.name for x in params]
        c = func.get_parameter("c")
        assert c.default == '"hello"'
        assert c.type == "str"
