from codegen_sdk.codebase.factory.get_session import get_codebase_graph_session
from codegen_sdk.enums import ProgrammingLanguage


def test_global_var_attribute(tmpdir) -> None:
    content = """
const A = Thing()

function foo() {}

A.bar = foo()
"""
    with get_codebase_graph_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": content}) as G:
        file = G.get_file("test.ts")
        assert len(file.global_vars) == 2
        foo = file.get_function("foo")
        assert len(foo.symbol_usages) == 1
        A = file.get_symbol("A")
        assert len(A.symbol_usages) == 1
