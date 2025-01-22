from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.dataclasses.usage import UsageType


def test_global_var_usages(tmpdir) -> None:
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
    # language=python
    content4 = """
from dir.file3 import file1 as indirect_file1

def quux(x, y):
    return indirect_file1.global_var
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3, "dir/file4.py": content4}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        file3 = codebase.get_file("dir/file3.py")
        file4 = codebase.get_file("dir/file4.py")
        foo = file1.get_function("foo")
        global_var = file1.get_global_var("global_var")
        aliased_global_var_imp = file2.get_import("imported_global_var")
        baz = file2.get_function("baz")
        buzz = file3.get_function("buzz")
        quux = file4.get_function("quux")
        file1_imp = file3.get_import("file1")
        indirect_file1_imp = file4.get_import("indirect_file1")

        assert {u.name for u in global_var.symbol_usages(UsageType.DIRECT)} == {"foo", "imported_global_var"}
        assert len(global_var.symbol_usages(UsageType.DIRECT)) == 2
        assert set(global_var.symbol_usages) == {foo, aliased_global_var_imp, baz, buzz, quux}
        assert len(global_var.symbol_usages) == 5


def test_global_var_module_import_usages(tmpdir) -> None:
    # language=python
    content1 = """
global_var = 1
other_var = 2
    """
    # language=python
    content2 = """
import dir.file1 as FF

def foo():
    return FF.global_var

def bar():
    return FF.other_var
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2}) as codebase:
        file1 = codebase.get_file("dir/file1.py")
        file2 = codebase.get_file("dir/file2.py")
        global_var = file1.get_global_var("global_var")
        file1_imp = file2.get_import("FF")

        assert set(u.match.source for u in global_var.usages) == {"FF.global_var"}
        assert len(global_var.symbol_usages(UsageType.DIRECT)) == 0
        assert len(global_var.usages) == 1

        assert set(u.match.source for u in file1_imp.usages) == {"FF", "FF"}
        assert set(file1_imp.symbol_usages(UsageType.DIRECT)) == {file2.get_function("foo"), file2.get_function("bar")}
        assert len(file1_imp.usages) == 2
