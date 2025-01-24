from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.dataclasses.usage import UsageType


def test_function_usages_recursive_function(tmpdir) -> None:
    # language=python
    content = """
def foo():
    return foo()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo_function = file.get_function("foo")
        assert len(foo_function.symbol_usages) == 1
        usage = foo_function.symbol_usages[0]
        assert usage is foo_function


def test_function_usages_basic(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    return 1

def bar():
    return foo()
    """
    # language=python
    content2 = """
from file1 import foo

def baz():
    return foo()
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        foo_function = file1.get_function("foo")
        bar_function = file1.get_function("bar")
        baz_function = file2.get_function("baz")

        assert len(foo_function.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 2
        assert len(foo_function.symbol_usages) == 3
        assert len(bar_function.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)) == 0
        assert len(baz_function.symbol_usages) == 0
        assert foo_function.symbol_usages(UsageType.DIRECT | UsageType.CHAINED)[0] is bar_function
        assert set(foo_function.symbol_usages) == {bar_function, file2.get_import("foo"), baz_function}


def test_function_usages_aliased(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    return 1

def bar():
    return foo()
    """
    # language=python
    content2 = """
from file1 import foo as foo2

def baz():
    return foo2()
    """
    # language=python
    content3 = """
from file1 import foo

def baz2():
    return foo()
        """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, "file3.py": content3}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")
        foo_function = file1.get_function("foo")
        bar_function = file1.get_function("bar")
        baz_function = file2.get_function("baz")
        baz2_function = file3.get_function("baz2")
        direct_usages = {bar_function, file2.get_import("foo2"), file3.get_import("foo")}
        indirect_usages = {baz2_function}
        aliased_usages = {baz_function}
        assert set(foo_function.symbol_usages(usage_types=UsageType.DIRECT)) == direct_usages, direct_usages
        assert set(foo_function.symbol_usages(usage_types=UsageType.INDIRECT)) == indirect_usages, set(foo_function.symbol_usages(usage_types=UsageType.INDIRECT))
        assert set(foo_function.symbol_usages(usage_types=UsageType.ALIASED)) == aliased_usages
        assert set(foo_function.symbol_usages(usage_types=UsageType.DIRECT | UsageType.INDIRECT)) == direct_usages | indirect_usages
        assert set(foo_function.symbol_usages(usage_types=UsageType.INDIRECT | UsageType.ALIASED)) == aliased_usages | indirect_usages
        assert set(foo_function.symbol_usages(usage_types=UsageType.DIRECT | UsageType.INDIRECT | UsageType.ALIASED)) == direct_usages | indirect_usages | aliased_usages
