from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.function import Function


def test_move_to_file_add_back_edge(tmpdir) -> None:
    # language=python
    content1 = """
def external_dep():
    return 42
"""
    # language=python
    content2 = """
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
    content3 = """
from file2 import bar

def baz():
    return bar() + 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, "file3.py": content3}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar = file2.get_function("bar")
        bar.move_to_file(file3, include_dependencies=True, strategy="add_back_edge")

    assert file1.content == content1
    # language=python
    assert (
        file2.content
        == """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24
"""
    )

    # language=python
    assert (
        file3.content
        == """
from file1 import external_dep
def baz():
    return bar() + 1

def bar_dep():
    return 2

def bar():
    return external_dep() + bar_dep()
"""
    )


def test_move_to_file_update_all_imports(tmpdir) -> None:
    # language=python
    content1 = """
def external_dep():
    return 42
"""
    # language=python
    content2 = """
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
    content3 = """
from file2 import bar

def baz():
    return bar() + 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, "file3.py": content3}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file("file3.py")

        bar = file2.get_function("bar")
        bar.move_to_file(file3, include_dependencies=True, strategy="update_all_imports")

    assert file1.content == content1
    # language=python
    assert (
        file2.content
        == """
from file1 import external_dep

def foo():
    return foo_dep() + 1

def foo_dep():
    return 24
"""
    )
    # language=python
    assert (
        file3.content
        == """
from file1 import external_dep
def baz():
    return bar() + 1

def bar_dep():
    return 2

def bar():
    return external_dep() + bar_dep()
"""
    )


def test_move_to_file_backedge_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.py"
    BAR_FILENAME = "bar_test_move_to_file.py"
    BAZ_FILENAME = "baz_test_move_to_file.py"

    # language=python
    FOO_FILE_CONTENT = """
def foo():
    return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
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
    BAZ_FILE_CONTENT = """
from bar_test_move_to_file import bar

def baz():
    '''uses bar'''
    return bar()
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.py
    # --------------------------------------
    #
    # def foo():
    #    return 1
    #
    # def abc():
    #    '''dependency, gets moved'''
    #    return 'abc'
    #
    # @my_decorator
    # def bar():
    #    '''gets moved'''
    #    return abc()
    #

    # --------------------------------------
    # bar_test_move_to_file.py
    # --------------------------------------
    #
    #
    # def xyz():
    #    '''should stay'''
    #    return 3
    #

    # --------------------------------------
    # baz_test_move_to_file.py
    # --------------------------------------
    #
    # from bar_test_move_to_file import bar
    #
    # def baz():
    #    '''uses bar'''
    #    return bar()
    #
    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
            BAZ_FILENAME: BAZ_FILE_CONTENT,
        },
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="add_back_edge", include_dependencies=True)

    # Check foo_test_move_to_file
    assert "def foo():" in foo_file.content
    assert "def abc():" in foo_file.content
    assert "@my_decorator" in foo_file.content
    assert "def bar():" in foo_file.content
    assert "return abc()" in foo_file.content
    assert codebase.get_symbol("foo").file == foo_file
    assert codebase.get_symbol("abc").file == foo_file
    assert codebase.get_symbol("bar").file == foo_file

    # Check bar_test_move_to_file
    assert "def abc():" not in bar_file.content
    assert "@my_decorator" not in bar_file.content
    assert "def bar():" not in bar_file.content
    assert "return abc()" not in bar_file.content
    assert "def xyz():" in bar_file.content
    assert codebase.get_symbol("xyz").file == bar_file
    assert "from foo_test_move_to_file import bar" in bar_file.content
    assert "from foo_test_move_to_file import abc" not in bar_file.content

    # check baz_test_move_to_file
    assert "from bar_test_move_to_file import bar" in baz_file.content
    assert "from foo_test_move_to_file import bar" not in baz_file.content
    assert "def baz():" in baz_file.content
    assert "return bar()" in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    new_symbol = foo_file.get_symbol("bar")
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_to_file_update_imports_without_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.py"
    BAR_FILENAME = "bar_test_move_to_file.py"
    BAZ_FILENAME = "baz_test_move_to_file.py"

    # language=python
    FOO_FILE_CONTENT = """
def foo():
    return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
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
    BAZ_FILE_CONTENT = """
from bar_test_move_to_file import bar

def baz():
    '''uses bar'''
    return bar()
    """

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
            BAZ_FILENAME: BAZ_FILE_CONTENT,
        },
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=False)

    # Check foo_test_move_to_file
    # language=python
    assert (
        foo_file.content.strip()
        == """
from bar_test_move_to_file import abc

def foo():
    return 1

@my_decorator
def bar():
    '''gets moved'''
    return abc()
""".strip()
    )
    # language=python
    assert (
        bar_file.content
        == """
def abc():
    '''dependency, DOES NOT GET MOVED'''
    return 'abc'

def xyz():
    '''should stay'''
    return 3
    """
    )
    # language=python
    assert (
        baz_file.content
        == """
from foo_test_move_to_file import bar
def baz():
    '''uses bar'''
    return bar()
    """
    )


def test_move_global_var(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.py"
    BAR_FILENAME = "bar_test_move_to_file.py"

    # language=python
    FOO_FILE_CONTENT = """
    """

    # language=python
    BAR_FILE_CONTENT = """
    from import1 import thing1
    from import2 import thing2, thing3

    GLOBAL = thing1(thing2, arg=thing3)
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.py
    # --------------------------------------
    #
    # from import2 import thing2, thing3
    # from import1 import thing1
    #
    # GLOBAL = thing1(thing2, arg=thing3)
    #

    # --------------------------------------
    # bar_test_move_to_file.py
    # --------------------------------------
    #
    #

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
        },
        commit=True,
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)

        global_symbol = bar_file.get_symbol("GLOBAL")
        global_symbol.move_to_file(foo_file, strategy="add_back_edge", include_dependencies=True)

    # Check foo_test_move_to_file
    assert "from import2 import thing2, thing3" in foo_file.content
    assert "from import1 import thing1" in foo_file.content
    assert "GLOBAL = thing1(thing2, arg=thing3)" in foo_file.content
    assert codebase.get_symbol("GLOBAL").file == foo_file

    # Check bar_test_move_to_file
    assert "from foo_test_move_to_file import GLOBAL" not in bar_file.content
    # We don't automatically remove unusued imports so lets leaf
    assert "from import1 import thing1" in bar_file.content
    assert "from import2 import thing2, thing3" in bar_file.content
    assert "GLOBAL = thing1(thing2, arg=thing3)" not in bar_file.content


def test_move_to_file_with_imports(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.py"
    BAR_FILENAME = "bar_test_move_to_file.py"

    # language=python
    FOO_FILE_CONTENT = """
    def foo():
        return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
    from import1 import thing1
    from import2 import thing2

    GLOBAL = thing1()

    def bar():
        return GLOBAL

    def baz():
        return thing1() + thing2()
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.py
    # --------------------------------------
    #
    # from import1 import thing1
    #
    # def foo():
    #     return 1
    #
    # GLOBAL = thing1()
    #
    # def bar():
    #     return GLOBAL
    #

    # --------------------------------------
    # bar_test_move_to_file.py
    # --------------------------------------
    #
    # from import1 import thing1
    # from import2 import thing2
    #
    # def baz():
    #     return thing1() + thing2()
    #

    with get_codebase_session(
        tmpdir=tmpdir,
        files={FOO_FILENAME: FOO_FILE_CONTENT, BAR_FILENAME: BAR_FILE_CONTENT},
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="add_back_edge", include_dependencies=True)

    # Check foo_test_move_to_file
    assert "from import1 import thing1" in foo_file.content
    assert "def foo():" in foo_file.content
    assert "GLOBAL = thing1()" in foo_file.content
    assert "def bar():" in foo_file.content
    assert "return GLOBAL" in foo_file.content
    assert codebase.get_symbol("foo").file == foo_file
    assert codebase.get_symbol("GLOBAL").file == foo_file
    assert codebase.get_symbol("bar").file == foo_file

    # Check bar_test_move_to_file
    assert "from foo_test_move_to_file import bar" not in bar_file.content
    assert "from foo_test_move_to_file import GLOBAL" not in bar_file.content
    assert "from import1 import thing1" in bar_file.content
    assert "from import2 import thing2" in bar_file.content
    assert "def baz():" in bar_file.content
    assert "return thing1() + thing2()" in bar_file.content
    assert codebase.get_symbol("baz").file == bar_file
    assert codebase.get_symbol("bar").file != bar_file
    assert codebase.get_symbol("GLOBAL").file != bar_file
    assert "def bar():" not in bar_file.content
    assert "return GLOBAL" not in bar_file.content
    assert "GLOBAL = thing1()" not in bar_file.content


def test_move_to_file_update_imports_include_deps(tmpdir) -> None:
    FOO_FILENAME = "foo_test_move_to_file.py"
    BAR_FILENAME = "bar_test_move_to_file.py"
    BAZ_FILENAME = "baz_test_move_to_file.py"

    # language=python
    FOO_FILE_CONTENT = """
    def foo():
        return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
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
    BAZ_FILE_CONTENT = """
    from bar_test_move_to_file import bar

    def baz():
        '''uses bar'''
        return bar()
    """

    ########################################
    # Intended Files After Move
    ########################################

    # --------------------------------------
    # foo_test_move_to_file.py
    # --------------------------------------
    #
    # def foo():
    #    return 1
    #
    # def abc():
    #    '''dependency, gets moved'''
    #    return 'abc'
    #
    # @my_decorator
    # def bar():
    #    '''gets moved'''
    #    return abc()
    #

    # --------------------------------------
    # bar_test_move_to_file.py
    # --------------------------------------
    #
    # def xyz():
    #    '''should stay'''
    #    return 3
    #

    # --------------------------------------
    # baz_test_move_to_file.py
    # --------------------------------------
    #
    # from foo_test_move_to_file import bar
    #
    # def baz():
    #    '''uses bar'''
    #    return bar()
    #

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
            BAZ_FILENAME: BAZ_FILE_CONTENT,
        },
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_symbol = bar_file.get_symbol("bar")
        bar_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=True)

    # Check foo_test_move_to_file
    assert "def foo():" in foo_file.content
    assert "def abc():" in foo_file.content
    assert "@my_decorator" in foo_file.content
    assert "def bar():" in foo_file.content
    assert "return abc()" in foo_file.content
    assert codebase.get_symbol("foo").file == foo_file
    assert codebase.get_symbol("abc").file == foo_file
    assert codebase.get_symbol("bar").file == foo_file

    # Check bar_test_move_to_file
    assert "def abc():" not in bar_file.content
    assert "@my_decorator" not in bar_file.content
    assert "def bar():" not in bar_file.content
    assert "return abc()" not in bar_file.content
    assert "def xyz():" in bar_file.content
    assert codebase.get_symbol("xyz").file == bar_file
    assert "from foo_test_move_to_file import bar" not in bar_file.content
    assert "from foo_test_move_to_file import abc" not in bar_file.content

    # check baz_test_move_to_file
    assert "from foo_test_move_to_file import bar" in baz_file.content
    assert "from bar_test_move_to_file import bar" not in baz_file.content
    assert "def baz():" in baz_file.content
    assert "return bar()" in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    new_symbol = foo_file.get_symbol("bar")
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar"
    assert isinstance(new_symbol, Function)


def test_move_to_file_module_import(tmpdir) -> None:
    FOO_FILENAME = "app/foo.py"
    BAR_FILENAME = "app/bar.py"
    BAZ_FILENAME = "app/baz.py"

    # language=python
    FOO_FILE_CONTENT = """
    def foo_func():
        return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
    @my_decorator
    def bar_func():
        print("I'm getting moved")
    """

    # language=python
    BAZ_FILE_CONTENT = """
    # module import of symbol to move
    from app import bar

    def baz():
        # usage of bar_func
        return bar.bar_func()
    """

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
            BAZ_FILENAME: BAZ_FILE_CONTENT,
        },
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_func_symbol = bar_file.get_symbol("bar_func")
        assert bar_func_symbol
        bar_func_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=True)

    # Check app/foo.py
    assert "def foo_func():" in foo_file.content
    assert "def bar_func():" in foo_file.content
    assert "@my_decorator" not in bar_file.content
    assert codebase.get_symbol("foo_func").file == foo_file
    assert codebase.get_symbol("bar_func").file == foo_file

    # Check app/bar.py
    assert "@my_decorator" not in bar_file.content
    assert "def bar_func():" not in bar_file.content

    # check baz_test_move_to_file
    assert "from app.foo import bar_func" in baz_file.content  # module import converted to symbol import
    assert "bar_func()" in baz_file.content
    assert "bar.bar_func()" not in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    new_symbol = foo_file.get_symbol("bar_func")
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar_func"
    assert isinstance(new_symbol, Function)


def test_move_to_file_external_module_dependency(tmpdir) -> None:
    FOO_FILENAME = "app/foo.py"
    BAR_FILENAME = "app/bar.py"
    BAZ_FILENAME = "app/baz.py"

    # language=python
    FOO_FILE_CONTENT = """
    def foo_func():
        return 1
    """

    # language=python
    BAR_FILE_CONTENT = """
    from app.foo import foo_func
    from typing import Optional

    @my_decorator
    def bar_func():
        foo_func()
        print(f"I'm getting moved")
    """

    # language=python
    BAZ_FILE_CONTENT = """
    # module import of symbol to move
    from app.bar import bar_func

    def baz():
        # usage of bar_func
        return bar_func()
    """

    with get_codebase_session(
        tmpdir=tmpdir,
        files={
            FOO_FILENAME: FOO_FILE_CONTENT,
            BAR_FILENAME: BAR_FILE_CONTENT,
            BAZ_FILENAME: BAZ_FILE_CONTENT,
        },
    ) as codebase:
        foo_file = codebase.get_file(FOO_FILENAME)
        bar_file = codebase.get_file(BAR_FILENAME)
        baz_file = codebase.get_file(BAZ_FILENAME)

        bar_func_symbol = bar_file.get_symbol("bar_func")
        assert bar_func_symbol
        bar_func_symbol.move_to_file(foo_file, strategy="update_all_imports", include_dependencies=True)

    # Check app/foo.py
    assert "def foo_func():" in foo_file.content
    assert "def bar_func():" in foo_file.content
    assert "@my_decorator" not in bar_file.content
    assert codebase.get_symbol("foo_func").file == foo_file
    assert codebase.get_symbol("bar_func").file == foo_file

    # Check app/bar.py
    assert "@my_decorator" not in bar_file.content
    assert "def bar_func():" not in bar_file.content

    # check baz_test_move_to_file
    assert "from app.foo import bar_func" in baz_file.content  # module import converted to symbol import
    assert "bar_func()" in baz_file.content
    assert "bar.bar_func()" not in baz_file.content
    assert codebase.get_symbol("baz").file == baz_file

    # Check new symbol
    new_symbol = foo_file.get_symbol("bar_func")
    assert new_symbol.file == foo_file
    assert new_symbol.name == "bar_func"
    assert isinstance(new_symbol, Function)


def test_function_move_to_file_circular_dependency(tmpdir) -> None:
    # language=python
    content1 = """
def foo():
    return bar() + 1

def bar():
    return foo() + 1
    """
    with get_codebase_session(tmpdir, files={"file1.py": content1}) as codebase:
        file1 = codebase.get_file("file1.py")
        foo = file1.get_function("foo")
        bar = file1.get_function("bar")
        assert bar in foo.dependencies
        assert foo in bar.dependencies

        file2 = codebase.create_file("file2.py", "")
        foo.move_to_file(file2, include_dependencies=True, strategy="add_back_edge")

    # language=python
    assert (
        file2.content.strip()
        == """
def bar():
    return foo() + 1

def foo():
    return bar() + 1
""".strip()
    )
    assert file1.content.strip() == ""


def test_move_to_file_update_all_imports_multi(tmpdir) -> None:
    # language=python
    content1 = """
def external_dep():
    return 42

def external_dep2():
    return 42
"""
    # language=python
    content2 = """
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
    file3_name = "file3.py"
    # language=python
    content3 = """
"""
    file4_name = "file4.py"
    # language=python
    content4 = """
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2, file3_name: content3, file4_name: content4}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")
        file3 = codebase.get_file(file3_name)
        file4 = codebase.get_file(file4_name)

        d1 = file1.get_function("external_dep")
        d2 = file1.get_function("external_dep2")
        d1.move_to_file(file3, include_dependencies=True, strategy="update_all_imports")
        d2.move_to_file(file4, include_dependencies=True, strategy="update_all_imports")

    # language=python
    assert (
        file1.content.strip()
        == """
    """.strip()
    )
    # language=python
    assert (
        file3.content.strip()
        == """
def external_dep():
    return 42
""".strip()
    )
    # language=python
    assert (
        file4.content.strip()
        == """
def external_dep2():
    return 42
        """.strip()
    )
    # language=python
    assert (
        file2.content.strip()
        == """
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
    """.strip()
    )
