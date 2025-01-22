from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_add_decorator_to_class(tmpdir) -> None:
    # =====[ Simple ]=====
    # language=python
    content = """
class Foo:
    def foo(fun):
        return fun

class Bar:
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        class_symbol.add_decorator("@test_decorator")

    assert "@test_decorator\nclass Bar:" in file.content


def test_add_decorator_to_method_existing(tmpdir) -> None:
    # language=python
    content = """
class Bar:
    @old
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        class_symbol.get_method("bar").add_decorator("@new")
    # language=python
    assert (
        file.content
        == """
class Bar:
    @new
    @old
    def bar(fun):
        return fun
"""
    )


def test_add_decorator_to_method(tmpdir) -> None:
    # language=python
    content = """
class Bar:
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        class_symbol.get_method("bar").add_decorator("@new")
    # language=python
    assert (
        file.content
        == """
class Bar:
    @new
    def bar(fun):
        return fun
"""
    )


def test_add_decorator_to_class_unique(tmpdir) -> None:
    # =====[ Simple ]=====
    # language=python
    content = """
class Foo:
    def foo(fun):
        return fun

@test_decorator
class Bar:
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        assert not class_symbol.add_decorator("@test_decorator", skip_if_exists=True)
    assert file.content.count("@test_decorator") == 1
    assert "@test_decorator\nclass Bar:" in file.content


def test_add_decorator_to_class_unique_arg(tmpdir) -> None:
    # =====[ Simple ]=====
    # language=python
    content = """
class Foo:
    def foo(fun):
        return fun

class Bar:
    def bar(fun):
        return fun
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        class_symbol = file.get_class("Bar")
        class_symbol.add_decorator("@test_decorator")
        assert class_symbol.add_decorator("@test_decorator(a=1)", skip_if_exists=True)

    assert file.content.count("@test_decorator") == 2
    assert "@test_decorator(a=1)\nclass Bar:" in file.content
