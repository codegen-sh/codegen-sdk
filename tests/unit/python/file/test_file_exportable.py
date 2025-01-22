from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.dataclasses.usage import UsageType
from graph_sitter.core.symbol import Symbol


def test_file_usages_basic(tmpdir) -> None:
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
"""
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content1, "dir/file2.py": content2, "dir/file3.py": content3, "dir/file4.py": content4}) as codebase:
        file1 = codebase.get_file("dir/file1.py")

        assert len(file1.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 1
        assert {u.source for u in file1.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)} == {"from dir import file1"}
        assert len(file1.symbol_usages) == 4
        assert {u.name if isinstance(u, Symbol) else u.source for u in file1.symbol_usages} == {"fuzz", "buzz", "from dir import file1", "from dir.file3 import file1 as indirect_file1"}
