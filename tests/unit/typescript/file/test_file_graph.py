from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.enums import ProgrammingLanguage


def test_graph_has_node_for_existing_file(tmpdir) -> None:
    # language=typescript
    content = """
function foo(bar: number): number {
    return bar;
}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")

        G = codebase.G
        assert G.has_node(file.node_id)
        assert G.get_node(file.node_id) == file
        assert G.has_node(file.node_id)
