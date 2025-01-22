from graph_sitter.codebase.factory.get_session import get_codebase_session
from tests.unit.python.utils.test_file_contents import file1_content, file2_content


def test_global_var_source(tmpdir) -> None:
    # language=python
    content = """
from a import b
from c.d import (e as f, g as h)

x = 5
y = 10
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        assert file.get_global_var("x").source == "x = 5"
        assert file.get_global_var("y").source == "y = 10"


def test_global_var_delete_then_insert_before(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.remove()
        foo.insert_before("bar = do_something()")

    # language=python
    assert (
        file.content
        == """
bar = do_something()

"""
    )


def test_global_var_insert_before_then_delete(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_before("bar = do_something()")
        foo.remove()

    # language=python
    assert (
        file.content
        == """
bar = do_something()

"""
    )


def test_global_var_insert_after_then_delete(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_after("bar = do_something()")
        foo.remove()

    # language=python
    assert (
        file.content
        == """

bar = do_something()
"""
    )


def test_global_var_edit_then_insert_before(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.edit("def foo():\n    print('Hello World!')")
        foo.insert_before("bar = do_something()")

    # language=python
    assert (
        file.content
        == """
bar = do_something()
def foo():
    print('Hello World!')
"""
    )


def test_global_var_edit_then_insert_after(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.edit("def foo():\n    print('Hello World!')")
        foo.insert_after("bar = do_something()")

    # language=python
    assert (
        file.content
        == """
def foo():
    print('Hello World!')
bar = do_something()
"""
    )


def test_global_var_insert_before_then_edit(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_before("bar = do_something()")
        foo.edit("def foo():\n    print('Hello World!')")

    # language=python
    assert (
        file.content
        == """
bar = do_something()
def foo():
    print('Hello World!')
"""
    )


def test_global_var_insert_after_then_edit(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_after("bar = do_something()")
        foo.edit("def foo():\n    print('Hello World!')")

    # language=python
    assert (
        file.content
        == """
def foo():
    print('Hello World!')
bar = do_something()
"""
    )


def test_global_var_multiple_insert_before(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_before("bar = do_something()")
        foo.insert_before("baz = do_something_else()")
        foo.insert_before("qux = do_something_else_else()")

    # language=python
    assert (
        file.content
        == """
bar = do_something()
baz = do_something_else()
qux = do_something_else_else()
foo = 1
"""
    )


def test_global_var_multiple_insert_after(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_after("bar = do_something()")
        foo.insert_after("baz = do_something_else()")
        foo.insert_after("qux = do_something_else_else()")

    # language=python
    assert (
        file.content
        == """
foo = 1
bar = do_something()
baz = do_something_else()
qux = do_something_else_else()
"""
    )


def test_global_var_transaction_priority(tmpdir) -> None:
    # language=python
    content = """
foo = 1
"""

    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo = file.get_symbol("foo")

        foo.insert_before("not_important()", priority=-1)
        foo.insert_before("something()")
        foo.insert_before("IMPORTANT()", priority=1)
        foo.insert_before("something_else()")

    # language=python
    assert (
        file.source
        == """IMPORTANT()
something()
something_else()
not_important()
foo = 1
"""
    )


def test_edit_global_var(tmpdir) -> None:
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": file1_content, "file2.py": file2_content}) as codebase:
        file1 = codebase.get_file("file1.py")

        # Move GLOBAL_CONSTANT_1 from file1 to file2
        global_var1 = file1.get_global_var("GLOBAL_CONSTANT_1")
        global_var1.rename("GLOBAL_CONSTANT_EDITED")

    assert "GLOBAL_CONSTANT_EDITED = 10" in file1.content


def test_edit_type_alias(tmpdir) -> None:
    # language=python
    content = """
from typing import Union

def foo(x: Union[int, str]) -> Union[int, str]:
    return x

def bar(x: Union[int, str]) -> Union[int, str]:
    return x
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        if "Union" in [imp.name for imp in file.imports]:
            for editable in file.find("Union["):
                if editable.ts_node_type == "generic_type":
                    new_type = editable.source.replace("Union[", "").replace("]", "").replace(", ", " | ")
                    editable.replace(editable.source, new_type)

            union_import = file.get_import("Union")
            if union_import:
                union_import.remove()
    assert "Union" not in file.content
    assert "def foo(x: int | str) -> int | str:" in file.content
    assert "def bar(x: int | str) -> int | str:" in file.content


def test_edit_type_alias_with_subscript(tmpdir) -> None:
    # language=python
    content = """ from typing import Union, TypeAlias
Class_types: TypeAlias = Union[Type1, Type2, Type3]
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        if "Union" in [imp.name for imp in file.imports]:
            for editable in file.find("Union["):
                if editable.ts_node_type == "subscript":
                    types = editable.source[6:-1].split(",")
                    types = [t.strip() for t in types if t.strip()]
                    new_type = " | ".join(types)
                    if len(types) > 1:
                        new_type = f"({new_type})"
                    editable.replace(editable.source, new_type)
        union_import = file.get_import("Union")
        if union_import:
            union_import.remove()
    assert "Union" not in file.content
    assert "Class_types: TypeAlias = (Type1 | Type2 | Type3)" in file.content
