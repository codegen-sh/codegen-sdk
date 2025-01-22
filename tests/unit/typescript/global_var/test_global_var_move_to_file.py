from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.enums import ProgrammingLanguage


def test_global_var_move_to_file_global_var_deps_does_not_throw(tmpdir) -> None:
    # language=typescript
    src = """
let b: number = 1;

let a: number = b + 1
"""
    # language=typescript
    dest = """
"""
    # TODO: fix this test
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"src.ts": src, "dest.ts": dest}, verify_output=False) as codebase:
        src = codebase.get_file("src.ts")
        dest = codebase.get_file("dest.ts")
        a_symbol = src.get_symbol("a")
        b_symbol = src.get_symbol("b")
        assert b_symbol in a_symbol.dependencies
        a_symbol.move_to_file(dest, include_dependencies=True)
