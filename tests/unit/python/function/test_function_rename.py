from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_function_rename_updates_usages(tmpdir) -> None:
    # =====[ Simple ]=====
    # language=python
    file = """
def foo(bar):
    return bar

def baz():
    return foo(1) + foo(1)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": file}) as codebase:
        file = codebase.get_file("file.py")
        symbol = file.get_function("foo")
        symbol.rename("XYZ")

    assert "def XYZ(" in file.content
    assert "return XYZ(1) + XYZ(1)" in file.content


def test_function_rename_updates_all_usages(tmpdir) -> None:
    # language=python
    content1 = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

def introduce(name: str, age: int) -> str:
    greeting = greet(name)
    return f"{greeting} I am {age} years old."
"""
    # language=python
    content2 = """
from file1 import greet, introduce

def main():
    name = 'John'
    age = 25
    greeting = greet(name)
    print(greeting)
    introduction = introduce(name, age)
    print(introduction)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        symbol_for_rename = codebase.get_symbol("greet")
        symbol_for_rename.rename("offender")

    # language=python
    assert (
        codebase.get_file("file1.py").content
        == """
def offender(name: str) -> str:
    return f"Hello, {name}!"

def introduce(name: str, age: int) -> str:
    greeting = offender(name)
    return f"{greeting} I am {age} years old."
"""
    )
    # language=python
    assert (
        codebase.get_file("file2.py").content
        == """
from file1 import offender, introduce

def main():
    name = 'John'
    age = 25
    greeting = offender(name)
    print(greeting)
    introduction = introduce(name, age)
    print(introduction)
"""
    )


def test_function_renames_module_import_uses__bar(tmpdir) -> None:
    # language=python
    content1 = """
from dir import file2
from dir.file3 import file1

def foo(name: str) -> str:
    return file1.undefined() + file2.bar() + file1.foo()
"""
    # language=python
    content2 = """
from dir import file1

def bar():
    name = 'John'
    greeting = file1.foo(name)
    print(greeting)
"""
    # language=python
    content3 = """
from dir.file2 import file1

def buz():
    return file1.foo('John')
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")
        foo = codebase.get_symbol("foo")
        bar = codebase.get_symbol("bar")

        assert set(bar.symbol_usages) == {foo}
        assert set(bar.symbol_usages) == {foo}
        bar.rename("updated_bar")

    # language=python
    assert (
        file1.content
        == """
from dir import file2
from dir.file3 import file1

def foo(name: str) -> str:
    return file1.undefined() + file2.updated_bar() + file1.foo()
"""
    )
    # language=python
    assert (
        file2.content
        == """
from dir import file1

def updated_bar():
    name = 'John'
    greeting = file1.foo(name)
    print(greeting)
"""
    )
    assert file3.content == content3


def test_function_rename_recursive(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return foo()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_function("foo")
        assert set(foo.symbol_usages) == {foo}
        assert set(foo.symbol_usages) == {foo}
        foo.rename("bar")
    # language=python
    assert (
        file.content
        == """
def bar():
    return bar()
    """
    )


def test_function_renames_module_import_uses__foo(tmpdir) -> None:
    # language=python
    content1 = """
from dir import file2
from dir.file3 import file1

def foo(name: str) -> str:
    return file1.undefined() + file2.bar() + foo()
"""
    # language=python
    content2 = """
from dir import file1

def bar():
    name = 'John'
    greeting = file1.foo(name)
    print(greeting)
"""
    # language=python
    content3 = """
from dir.file2 import file1

def buz():
    return file1.foo('John')
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")
        foo = codebase.get_symbol("foo")
        bar = codebase.get_symbol("bar")

        assert set(foo.symbol_usages) == {bar, file3.get_function("buz"), foo}
        assert set(foo.symbol_usages) == {bar, file3.get_function("buz"), foo}
        foo.rename("updated_foo")

    # language=python
    assert (
        file1.content
        == """
from dir import file2
from dir.file3 import file1

def updated_foo(name: str) -> str:
    return file1.undefined() + file2.bar() + updated_foo()
"""
    )
    # language=python
    assert (
        file2.content
        == """
from dir import file1

def bar():
    name = 'John'
    greeting = file1.updated_foo(name)
    print(greeting)
"""
    )
    # language=python
    assert (
        file3.content
        == """
from dir.file2 import file1

def buz():
    return file1.updated_foo('John')
    """
    )


def test_function_rename_updates_module_import_loops(tmpdir) -> None:
    # language=python
    content1 = """
from dir import file2
from dir.file3 import file1

def foo(name: str) -> str:
    return file1.undefined() + file2.bar() + file1.foo()
"""
    # language=python
    content2 = """
from dir import file1

def bar():
    name = 'John'
    greeting = file1.foo(name)
    print(greeting)
"""
    # language=python
    content3 = """
from dir.file2 import file1

def buz():
    return file1.foo('John')
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")

        foo = codebase.get_symbol("foo")
        foo.rename("updated_foo")

        bar = codebase.get_symbol("bar")
        bar.rename("updated_bar")

    # language=python
    assert (
        file1.content
        == """
from dir import file2
from dir.file3 import file1

def updated_foo(name: str) -> str:
    return file1.undefined() + file2.updated_bar() + file1.updated_foo()
"""
    )
    # language=python
    assert (
        file2.content
        == """
from dir import file1

def updated_bar():
    name = 'John'
    greeting = file1.updated_foo(name)
    print(greeting)
"""
    )
    # language=python
    assert (
        file3.content
        == """
from dir.file2 import file1

def buz():
    return file1.updated_foo('John')
    """
    )
