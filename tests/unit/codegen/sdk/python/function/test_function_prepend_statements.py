from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_function_prepend_statement(tmpdir) -> None:
    # language=python
    content = """
def foo(x, y):
    a = x + y
    b = x - y

class MyClass:
    def bar(self, x, y):
        a = x + y
        b = x - y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        bar = file.get_class("MyClass").get_method("bar")

        bar.prepend_statements("print(y)")
        foo.prepend_statements("print(x)")

    # language=python
    new_content = """
def foo(x, y):
    print(x)
    a = x + y
    b = x - y

class MyClass:
    def bar(self, x, y):
        print(y)
        a = x + y
        b = x - y
    """
    assert file.content == new_content


def test_function_add_statements(tmpdir) -> None:
    # language=python
    content = """
def foo(x, y):
    a = x + y
    b = x - y

class MyClass:
    def bar(self, x, y):
        a = x + y
        b = x - y
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        bar = file.get_class("MyClass").get_method("bar")

        bar.add_statements("print(y)")
        foo.add_statements("print(x)")

    # language=python
    new_content = """
def foo(x, y):
    a = x + y
    b = x - y
    print(x)

class MyClass:
    def bar(self, x, y):
        a = x + y
        b = x - y
        print(y)
    """
    assert file.content == new_content
