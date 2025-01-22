from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.python import PyAssignment


def test_file_add_symbol_from_source_updates_graph(tmpdir) -> None:
    # language=python
    content = """
def foo(bar):
    return bar
"""

    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")

        file.add_symbol_from_source(source="c = 1")

    symbol = file.get_symbol("c")

    assert symbol.name == "c"
    assert isinstance(symbol, PyAssignment)
    assert "c = 1" in file.content

    assert any([node.name == "c" for node in file.get_nodes()])
