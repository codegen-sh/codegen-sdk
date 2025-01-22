from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_nested_base(tmpdir) -> None:
    # language=python
    content = """
def parent():
    def a():
        pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        parent = codebase.get_symbol("parent")
        assert len(parent.nested_functions) == 1
        assert parent.nested_functions[0].name == "a"
        assert parent.code_block.level == 1
        assert parent.nested_functions[0].code_block.level == 2


def test_nested_parsing(tmpdir) -> None:
    # language=python
    content = """
def a():
    pass

def parent():
    def b():
        pass

    def c():
        pass

    def d():
        def e():
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        parent = codebase.get_symbol("parent")
        assert len(parent.nested_functions) == 3
        assert {f.name for f in parent.nested_functions} == {"b", "c", "d"}


def test_usages(tmpdir) -> None:
    # language=python
    content = """
def a():
    pass

def parent():
    def b():
        pass

    a()
    b()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        parent = codebase.get_symbol("parent")
        a = codebase.get_symbol("a")
        assert len(a.symbol_usages) == 1
        assert a.symbol_usages[0] == parent

        b = parent.nested_functions[0]
        assert len(b.symbol_usages) == 1
        assert b.symbol_usages[0] == parent


def test_dependencies(tmpdir) -> None:
    # language=python
    content = """
def a():
    pass

def parent():
    def b():
        a()

    a()
    b()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        parent = codebase.get_symbol("parent")
        a = codebase.get_symbol("a")
        assert len(a.dependencies) == 0

        b = parent.nested_functions[0]
        assert len(b.dependencies) == 1
        assert b.dependencies[0] == a

        assert len(parent.dependencies) == 1
        assert {d.name for d in parent.dependencies} == {"a"}


def test_nested(tmpdir) -> None:
    # language=python
    content = """
def parent():
    def a():
        def b():
            def c():
                pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        parent = codebase.get_symbol("parent")
        assert len(parent.nested_functions) == 1
        assert parent.code_block.level == 1

        a = parent.nested_functions[0]
        assert len(a.nested_functions) == 1
        assert a.code_block.level == 2

        b = a.nested_functions[0]
        assert len(b.nested_functions) == 1
        assert b.code_block.level == 3

        c = b.nested_functions[0]
        assert len(c.nested_functions) == 0
        assert c.code_block.level == 4


def test_similarity(tmpdir) -> None:
    # language=python
    content = """
def foo():
    def a():
        def b():
            pass
def bar():
    def a():
        def b():
            pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        b1 = codebase.get_symbol("foo").nested_functions[0].nested_functions[0]
        b2 = codebase.get_symbol("bar").nested_functions[0].nested_functions[0]
        assert b1 != b2
