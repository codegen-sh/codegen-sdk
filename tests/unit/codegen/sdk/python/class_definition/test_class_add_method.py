from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session

if TYPE_CHECKING:
    from codegen.sdk.python import PyClass, PyFile


def test_add_method_basic(tmpdir) -> None:
    # language=python
    content = """
class Abc():
    def foo(a, b, c):
        return a + b + c
"""
    # language=python
    content2 = """
def test():
    foo(1, 2, 3)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(content2)

    # language=python
    assert (
        file.content
        == """
class Abc():
    def foo(a, b, c):
        return a + b + c

    def test():
        foo(1, 2, 3)
"""
    )


def test_add_method_after_method_with_docstring(tmpdir) -> None:
    # language=python
    content = """
class Abc():
    \"\"\"Docstring\"\"\"
    def foo(a, b, c):
        return a + b + c
"""
    # language=python
    content2 = """
def test():
    foo(1, 2, 3)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(content2)

    # language=python
    assert (
        file.content
        == """
class Abc():
    \"\"\"Docstring\"\"\"
    def foo(a, b, c):
        return a + b + c

    def test():
        foo(1, 2, 3)
"""
    )


def test_add_method_multiple_times(tmpdir) -> None:
    # language=python
    content = """
class Abc():
    def foo(a, b, c):
        return a + b + c
"""
    # language=python
    content2 = """
def test():
    foo(1, 2, 3)
"""
    # language=python
    content3 = """
def test2():
    foo(4, 5, 6)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(content2)
        foo.methods.append(content3)

    # language=python
    assert (
        file.content
        == """
class Abc():
    def foo(a, b, c):
        return a + b + c

    def test():
        foo(1, 2, 3)

    def test2():
        foo(4, 5, 6)
"""
    )


def test_add_method_out_of_order(tmpdir) -> None:
    # language=python
    content = """
class Abc():
    def foo(a, b, c):
        return a + b + c
"""
    # language=python
    content2 = """
def test2():
    foo(1, 2, 3)
"""
    # language=python
    content3 = """
def test3():
    foo(4, 5, 6)
"""
    # language=python
    content4 = """
def test4():
    foo(7, 8, 9)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.insert(0, content2)
        foo.methods.insert(2, content3)
        foo.methods.insert(0, content4)

    # language=python
    assert (
        file.content
        == """
class Abc():

    def test4():
        foo(7, 8, 9)

    def test2():
        foo(1, 2, 3)

    def foo(a, b, c):
        return a + b + c

    def test3():
        foo(4, 5, 6)
"""
    )


def test_add_first_method_with_no_methods(tmpdir) -> None:
    # language=python
    content = """
@decorator
class Abc():
    attr: str = "test"
"""
    # language=python
    new_method = """
def test2():
    foo(1, 2, 3)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(new_method)

    # language=python
    assert (
        file.content
        == """
@decorator
class Abc():
    attr: str = "test"

    def test2():
        foo(1, 2, 3)
"""
    )


def test_append_multiple_method_with_no_methods(tmpdir) -> None:
    # language=python
    content = """
@decorator
class Abc():
    attr: str = "test"
"""
    # language=python
    content2 = """
def test2():
    foo(1, 2, 3)
"""
    # language=python
    content3 = """
def test3():
    foo(2, 3, 4)
"""
    # language=python
    content4 = """
def test4():
    foo(4, 5, 6)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(content2)
        foo.methods.append(content3)
        foo.methods.append(content4)

    # language=python
    assert (
        file.content
        == """
@decorator
class Abc():
    attr: str = "test"

    def test2():
        foo(1, 2, 3)

    def test3():
        foo(2, 3, 4)

    def test4():
        foo(4, 5, 6)
"""
    )


def test_insert_multiple_method_with_no_methods(tmpdir) -> None:
    # language=python
    content = """
@decorator
class Abc():
    attr: str = "test"
"""
    # language=python
    content2 = """
def test2():
    foo(1, 2, 3)
"""
    # language=python
    content3 = """
def test3():
    foo(2, 3, 4)
"""
    # language=python
    content4 = """
def test4():
    foo(4, 5, 6)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.append(content2)
        foo.methods.insert(0, content3)
        foo.methods.insert(0, content4)

    # language=python
    assert (
        file.content
        == """
@decorator
class Abc():
    attr: str = "test"

    def test4():
        foo(4, 5, 6)

    def test3():
        foo(2, 3, 4)

    def test2():
        foo(1, 2, 3)
"""
    )


def test_insert_methods_out_of_order_with_no_methods(tmpdir) -> None:
    # language=python
    content = """
@decorator
class Abc():
    attr: str = "test"
"""
    # language=python
    content2 = """
def test2():
    foo(1, 2, 3)
"""
    # language=python
    content3 = """
def test3():
    foo(2, 3, 4)
"""
    # language=python
    content4 = """
def test4():
    foo(4, 5, 6)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        foo = file.get_class("Abc")
        foo.methods.insert(2, content2)
        foo.methods.insert(0, content3)
        foo.methods.insert(1, content4)

    # language=python
    assert (
        file.content
        == """
@decorator
class Abc():
    attr: str = "test"

    def test3():
        foo(2, 3, 4)

    def test4():
        foo(4, 5, 6)

    def test2():
        foo(1, 2, 3)
"""
    )


def test_add_method_with_symbol(tmpdir) -> None:
    # language=python
    content = """
def top_level_function():
    print("Hello, world!")

class Abc():
    def foo(a, b, c):
        return a + b + c
"""
    # language=python
    content2 = """
class Efg():
    def test():
        foo(1, 2, 3)
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content, "file2.py": content2}) as codebase:
        file1: PyFile = codebase.get_file("file1.py")
        file2: PyFile = codebase.get_file("file2.py")
        abc = file1.get_class("Abc")
        efg: PyClass = file2.get_class("Efg")
        abc.methods.append(efg.get_method("test"))
        abc.methods.append(file1.get_function("top_level_function"))

    # language=python
    assert (
        file1.content
        == """
def top_level_function():
    print("Hello, world!")

class Abc():
    def foo(a, b, c):
        return a + b + c

    def test():
        foo(1, 2, 3)

    def top_level_function():
        print("Hello, world!")
"""
    )


def test_add_method_in_middle(tmpdir) -> None:
    # language=python
    content = """
class Abc():
    attr: str = "test"

    def test1():
        foo(1, 2, 3)

    def test2():
        foo(2, 3, 4)

    def test4():
        foo(4, 5, 6)
"""
    # language=python
    content2 = """
def test3():
    foo(3, 4, 5)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        abc = file.get_class("Abc")
        abc.methods.insert(2, content2)

    # language=python
    assert (
        file.content
        == """
class Abc():
    attr: str = "test"

    def test1():
        foo(1, 2, 3)

    def test2():
        foo(2, 3, 4)

    def test3():
        foo(3, 4, 5)

    def test4():
        foo(4, 5, 6)
"""
    )
