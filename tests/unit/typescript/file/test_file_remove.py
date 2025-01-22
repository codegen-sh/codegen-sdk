import os

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.enums import ProgrammingLanguage


def tets_remove_existing_file(tmpdir) -> None:
    # language=typescript
    content = """
function foo(bar: number): number {
    return bar;
}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        file.remove()

    assert not os.path.exists(file.filepath)
