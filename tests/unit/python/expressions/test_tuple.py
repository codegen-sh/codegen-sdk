from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.symbol_groups.tuple import Tuple


def test_tuple_basic(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = (a, b, c)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: Tuple = symbol.value
        for child in symbol_list:
            assert child
        assert symbol_list[0] == "a"
        assert symbol_list[1] == "b"
        assert symbol_list[2] == "c"
        del symbol_list[1]
        symbol_list.append("d")
    # language=python
    assert (
        file.content
        == """
symbol = (a, c, d)
"""
    )


def test_tuple_multiline(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = (
    a,
    b,
    c,
)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: Tuple = symbol.value
        for child in symbol_list:
            assert child
        assert symbol_list[0] == "a"
        assert symbol_list[1] == "b"
        assert symbol_list[2] == "c"
        del symbol_list[1]
        symbol_list.append("d")
        symbol_list.append("e")
    # language=python
    assert (
        file.content
        == """
symbol = (
    a,
    c,
    d,
    e,
)
"""
    )
