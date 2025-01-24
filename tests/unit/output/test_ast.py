from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_ast_basic(tmpdir: str, snapshot) -> None:
    # language=python
    content = """
class Foo:
    def foo(fun):
        return fun

class Bar:
    bar: int = 0
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        foo_class = file.get_class("Foo")
        ast = foo_class.ast()
        snapshot.assert_match(ast.model_dump_json(indent=4) + "\n", "ast.json")


def test_ast_nested(tmpdir: str, snapshot) -> None:
    # language=python
    content = """
class Foo:
    class Bar:
        def baz(self):
            pass
"""
    with get_codebase_session(
        tmpdir=tmpdir,
        files={"test.py": content},
    ) as codebase:
        file = codebase.get_file("test.py")
        foo_class = file.get_class("Foo")
        ast = foo_class.ast()
        snapshot.assert_match(ast.model_dump_json(indent=4) + "\n", "ast-nested.json")
