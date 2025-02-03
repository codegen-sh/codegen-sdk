from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.function import Function


def test_move_to_file_update_all_imports(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def external_dep():
    return 42
"""

    # language=python
    FILE_2_CONTENT = """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24

def bar():
    return external_dep() + bar_dep()

def bar_dep():
    return 2
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    return bar() + 1
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
def external_dep():
    return 42
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file1 import external_dep
def baz():
    return bar() + 1

def bar_dep():
    return 2

def bar():
    return external_dep() + bar_dep()
"""
    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar = file2.get_function("bar")
        bar.move_to_file(file3, include_dependencies=True, strategy="update_all_imports")

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()


def test_move_to_file_update_all_imports_include_dependencies(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
def abc():
    '''dependency, gets moved'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
def foo():
    return 1

def abc():
    '''dependency, gets moved'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file1 import bar
def baz():
    '''uses bar'''
    return bar()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar_symbol = file2.get_symbol("bar")
        bar_symbol.move_to_file(file1, strategy="update_all_imports", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_to_file_update_all_imports_without_include_dependencies(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
def abc():
    '''dependency, DOES NOT GET MOVED'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
from file2 import abc

def foo():
    return 1

@my_decorator
def bar():
    '''gets moved'''
    return abc()
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
def abc():
    '''dependency, DOES NOT GET MOVED'''
    return 'abc'

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file1 import bar
def baz():
    '''uses bar'''
    return bar()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar_symbol = file2.get_symbol("bar")
        bar_symbol.move_to_file(file1, strategy="update_all_imports", include_dependencies=False)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_to_file_add_back_edge(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def external_dep():
    return 42
"""

    # language=python
    FILE_2_CONTENT = """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24

def bar():
    return external_dep() + bar_dep()

def bar_dep():
    return 2
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    return bar() + 1
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
def external_dep():
    return 42
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file1 import external_dep
def baz():
    return bar() + 1

def bar_dep():
    return 2

def bar():
    return external_dep() + bar_dep()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar = file2.get_function("bar")
        bar.move_to_file(file3, include_dependencies=True, strategy="add_back_edge")

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()


def test_move_to_file_add_back_edge_including_dependencies(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
def abc():
    '''dependency, gets moved'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
def foo():
    return 1

def abc():
    '''dependency, gets moved'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from file1 import bar

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
""".strip()

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar_symbol = file2.get_symbol("bar")
        bar_symbol.move_to_file(file1, strategy="add_back_edge", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_to_file_add_back_edge_without_including_dependencies(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
def abc():
    '''dependency, DOES NOT GET MOVED'''
    return 'abc'

@my_decorator
def bar():
    '''gets moved'''
    return abc()

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
from file2 import abc

def foo():
    return 1

@my_decorator
def bar():
    '''gets moved'''
    return abc()
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from file1 import bar

def abc():
    '''dependency, DOES NOT GET MOVED'''
    return 'abc'

def xyz():
    '''should stay'''
    return 3
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
from file2 import bar

def baz():
    '''uses bar'''
    return bar()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar_symbol = file2.get_symbol("bar")
        bar_symbol.move_to_file(file1, strategy="add_back_edge", include_dependencies=False)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_global_var(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
"""

    # language=python
    FILE_2_CONTENT = """
from import1 import thing1
from import2 import thing2, thing3

GLOBAL = thing1(thing2, arg=thing3)
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
from import1 import thing1
from import2 import thing2, thing3



GLOBAL = thing1(thing2, arg=thing3)
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from import1 import thing1
from import2 import thing2, thing3
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")

        global_symbol = file2.get_symbol("GLOBAL")
        global_symbol.move_to_file(file1, strategy="update_all_imports", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()


def test_move_to_file_with_imports(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
from import1 import thing1
from import2 import thing2

GLOBAL = thing1()

def bar():
    return GLOBAL

def baz():
    return thing1() + thing2()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
from import1 import thing1

def foo():
    return 1

GLOBAL = thing1()

def bar():
    return GLOBAL
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from import1 import thing1
from import2 import thing2

def baz():
    return thing1() + thing2()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")

        bar_symbol = file2.get_symbol("bar")
        bar_symbol.move_to_file(file1, strategy="add_back_edge", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()


def test_move_to_file_module_import(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo_func():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
@my_decorator
def bar_func():
    print("I'm getting moved")
"""

    # language=python
    FILE_3_CONTENT = """
# module import of symbol to move
from app import file2

def baz():
    # usage of bar_func
    return file2.bar_func()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
def foo_func():
    return 1

@my_decorator
def bar_func():
    print("I'm getting moved")
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
# module import of symbol to move
from app.file1 import bar_func
from app import file2

def baz():
    # usage of bar_func
    return bar_func()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "app/file1.py": FILE_1_CONTENT,
            "app/file2.py": FILE_2_CONTENT,
            "app/file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("app/file1.py")
        file2 = codebase.get_file("app/file2.py")
        file3 = codebase.get_file("app/file3.py")

        bar_func_symbol = file2.get_symbol("bar_func")
        assert bar_func_symbol
        bar_func_symbol.move_to_file(file1, strategy="update_all_imports", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar_func")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar_func"
    assert isinstance(new_symbol, Function)


def test_move_to_file_external_module_dependency(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo_func():
    return 1
"""

    # language=python
    FILE_2_CONTENT = """
from app.file1 import foo_func
from typing import Optional

@my_decorator
def bar_func():
    foo_func()
    print(f"I'm getting moved")
"""

    # language=python
    FILE_3_CONTENT = """
# module import of symbol to move
from app.file2 import bar_func

def baz():
    # usage of bar_func
    return bar_func()
"""

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
from app.file1 import foo_func

def foo_func():
    return 1

@my_decorator
def bar_func():
    foo_func()
    print(f"I'm getting moved")
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from app.file1 import foo_func
from typing import Optional
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
# module import of symbol to movefrom app.file1 import bar_func


def baz():
    # usage of bar_func
    return bar_func()
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "app/file1.py": FILE_1_CONTENT,
            "app/file2.py": FILE_2_CONTENT,
            "app/file3.py": FILE_3_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("app/file1.py")
        file2 = codebase.get_file("app/file2.py")
        file3 = codebase.get_file("app/file3.py")

        bar_func_symbol = file2.get_symbol("bar_func")
        assert bar_func_symbol
        bar_func_symbol.move_to_file(file1, strategy="update_all_imports", include_dependencies=True)

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()

    # Check new symbol
    new_symbol = file1.get_symbol("bar_func")
    assert new_symbol.file == file1
    assert new_symbol.name == "bar_func"
    assert isinstance(new_symbol, Function)


def test_function_move_to_file_circular_dependency(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def foo():
    return bar() + 1

def bar():
    return foo() + 1
    """

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
def bar():
    return foo() + 1

def foo():
    return bar() + 1
"""

    # ===============================

    with get_codebase_session(
        tmpdir,
        files={"file1.py": FILE_1_CONTENT},
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("file2.py", "")
        foo.move_to_file(file2, include_dependencies=True, strategy="add_back_edge")

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()


def test_move_to_file_update_all_imports_multi(tmpdir) -> None:
    # ========== [ BEFORE ] ==========
    # language=python
    FILE_1_CONTENT = """
def external_dep():
    return 42

def external_dep2():
    return 42
"""

    # language=python
    FILE_2_CONTENT = """
from file1 import external_dep, external_dep2

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24

def bar():
    return external_dep() + bar_dep() + external_dep2()

def bar_dep():
    return 2
"""

    # language=python
    FILE_3_CONTENT = """
"""

    # language=python
    FILE_4_CONTENT = """
    """

    # ========== [ AFTER ] ==========
    # language=python
    FILE_1_CONTENT_AFTER = """
"""

    # language=python
    FILE_2_CONTENT_AFTER = """
from file3 import external_dep
from file4 import external_dep2
def foo():
    return foo_dep() + 1

def foo_dep():
    return 24

def bar():
    return external_dep() + bar_dep() + external_dep2()

def bar_dep():
    return 2
"""

    # language=python
    FILE_3_CONTENT_AFTER = """
def external_dep():
    return 42
"""

    # language=python
    FILE_4_CONTENT_AFTER = """
def external_dep2():
    return 42
"""

    # ===============================

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            "file1.py": FILE_1_CONTENT,
            "file2.py": FILE_2_CONTENT,
            "file3.py": FILE_3_CONTENT,
            "file4.py": FILE_4_CONTENT,
        },
    ) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")
        file4 = codebase.get_file("file4.py")

        d1 = file1.get_function("external_dep")
        d2 = file1.get_function("external_dep2")
        d1.move_to_file(file3, include_dependencies=True, strategy="update_all_imports")
        d2.move_to_file(file4, include_dependencies=True, strategy="update_all_imports")

    assert file1.content.strip() == FILE_1_CONTENT_AFTER.strip()
    assert file2.content.strip() == FILE_2_CONTENT_AFTER.strip()
    assert file3.content.strip() == FILE_3_CONTENT_AFTER.strip()
    assert file4.content.strip() == FILE_4_CONTENT_AFTER.strip()
