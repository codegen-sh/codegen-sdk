from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.dataclasses.usage import UsageType


def test_function_usages_in_main(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return 1, 2

a = foo()
b, c = foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        assert len(file.global_vars) == 3
        assert len(foo.symbol_usages) == 3
        assert {usage.name for usage in foo.symbol_usages} == {"a", "b", "c"}


def test_function_usages_in_if(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return 1

if True:
    GLOBAL_VAR = foo()
elif False:
    GLOBAL_VAR_2 = foo()
else:
    GLOBAL_VAR_3 = foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_function("foo")

        assert len(file.global_vars) == 3
        assert len(foo.symbol_usages) == 3
        assert {usage.name for usage in foo.symbol_usages} == {"GLOBAL_VAR", "GLOBAL_VAR_2", "GLOBAL_VAR_3"}


def test_function_all_usages(tmpdir) -> None:
    # language=python
    file1_content = """
from file2 import bar

def foo(x: int, y: int) -> int:
    return x + y

def circular() -> int:
    return bar(1) + 123
    """
    # language=python
    file2_content = """
from file1 import foo

def bar(a: str) -> str:
    return str(foo(1, 2)) + a

def random() -> int:
    return 42 + foo(2,3)
    """
    # language=python
    file3_content = """
from file2 import random

def test_int() -> int:
    return random() + random()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": file1_content, "file2.py": file2_content, "file3.py": file3_content}) as codebase:
        foo_symbol = codebase.get_file("file1.py").get_function("foo")
        usages = foo_symbol.symbol_usages
        usages.sort(key=lambda symbol: symbol.name)
        assert [u.name for u in usages] == ["bar", "foo", "random"]


def test_function_usages_in_file_import(tmpdir) -> None:
    # language=python
    content1 = """
global_var = 1

def foo(x, y):
    a = x + y + global_var
    return a

def bar(x, y):
    return foo(x, y)
    """
    # language=python
    content2 = """
from dir.file1 import foo as imported_foo, global_var as imported_global_var

def baz(x, y):
    return imported_foo(x, y) + imported_global_var

def qux(x, y):
    return imported_foo(x, y)
    """
    # language=python
    content3 = """
from dir import file1

def fuzz(x, y):
    return file1.foo(x, y)

def buzz(x, y):
    return file1.global_var
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        foo = file1.get_function("foo")

        assert {u.name for u in foo.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)} == {"bar", "fuzz", "imported_foo"}
        assert len(foo.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 3
        assert {u.name for u in foo.symbol_usages} == {"bar", "imported_foo", "baz", "qux", "fuzz"}
        assert len(foo.symbol_usages) == 5


def test_function_usages_in_indirect_file_import(tmpdir) -> None:
    # language=python
    content1 = """
    global_var = 1

    def foo(x, y):
        a = x + y + global_var
        return a

    def bar(x, y):
        return foo(x, y)
        """
    # language=python
    content2 = """
    from dir import file1

    def fuzz(x, y):
        return file1.foo(x, y)

    def buzz(x, y):
        return file1.global_var
        """
    # language=python
    content3 = """
    from dir.file2 import file1 as indirect_file1

    def baz(x, y):
        return indirect_file1.foo(x, y)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        fuzz = file2.get_function("fuzz")
        buzz = file2.get_function("buzz")
        baz = file3.get_function("baz")
        file1_imp = file2.get_import("file1")
        file1_indirect_imp = file3.get_import("indirect_file1")

        assert set(foo.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == {bar, fuzz, baz}
        assert set(foo.symbol_usages) == {bar, fuzz, baz}
        assert set(file1_imp.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == {fuzz, buzz, file1_indirect_imp}
        assert set(file1_imp.symbol_usages) == {fuzz, buzz, file1_indirect_imp, baz}
        assert set(file1_indirect_imp.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == {baz}
        assert set(file1_indirect_imp.symbol_usages) == {baz}
        assert len(foo.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 3
        assert len(foo.symbol_usages) == 3


def test_function_all_usages_with_module_import_loop(tmpdir) -> None:
    # language=python
    content1 = """
from dir import file2

def bar():
    return file2.foo()
    """
    # language=python
    content2 = """
from dir import file1

def foo():
    return file1.bar()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        bar = file1.get_function("bar")
        foo = file2.get_function("foo")

        assert set(bar.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == {foo}
        assert len(bar.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 1
        assert set(bar.symbol_usages) == {foo}
        assert len(bar.symbol_usages) == 1


def test_function_usages_through_wildcard_import(tmpdir) -> None:
    content1 = """
from dir.file2 import * as
"""
