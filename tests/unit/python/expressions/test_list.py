from itertools import product

import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.symbol_groups.list import List


def test_list_basic(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = [a, b, c]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
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
symbol = [a, c, d]
"""
    )


def test_list_multiline(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = [
    a,
    b,
    c,
]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
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
symbol = [
    a,
    c,
    d,
    e,
]
"""
    )


def test_list_insert(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = [a, b, c]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        symbol_list.append("d")
    # language=python
    assert (
        file.content
        == """
symbol = [a, b, c, d]
"""
    )


cases = list(product(range(4), repeat=2))


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_list_interleaved(tmpdir, removes, inserts) -> None:
    ref_list = [-1 + -i for i in range(removes)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(max(inserts, removes)):
            if i < inserts:
                symbol_list.append(i)
                ref_list.append(i)
            if i < removes:
                del symbol_list[0]
                del ref_list[0]
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_list_interleaved_syncing(tmpdir, removes, inserts) -> None:
    ref_list = [-1 + -i for i in range(removes)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(max(inserts, removes)):
            if i < inserts:
                symbol_list.append(i)
            if i < removes:
                del symbol_list[0]
        codebase.commit(sync_graph=False)
        codebase.reset()
        for i in range(max(inserts, removes)):
            if i < inserts:
                symbol_list.append(i)
                ref_list.append(i)
            if i < removes:
                del symbol_list[0]
                del ref_list[0]
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_list_removes_first(tmpdir, removes, inserts) -> None:
    ref_list = [-1 + -i for i in range(removes)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(removes):
            del symbol_list[0]
            del ref_list[0]
        for i in range(inserts):
            symbol_list.append(i)
            ref_list.append(i)
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_list_inserts_first(tmpdir, removes, inserts) -> None:
    ref_list = [-1 + -i for i in range(removes)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(inserts):
            symbol_list.append(i)
            ref_list.append(i)
        for i in range(removes):
            del symbol_list[0]
            del ref_list[0]
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("existing,inserts", cases, ids=[f"{existing=}-{inserts=}" for existing, inserts in cases])
def test_list_append_existing(tmpdir, existing, inserts) -> None:
    ref_list = [-1 + -i for i in range(existing)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(inserts):
            symbol_list.append(i)
            ref_list.append(i)
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("existing,inserts", cases, ids=[f"existing={existing + 1}-{inserts=}" for existing, inserts in cases])
def test_list_insert_existing(tmpdir, existing, inserts) -> None:
    ref_list = [-1 + -i for i in range(existing + 1)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(inserts):
            symbol_list.insert(i, i)
            ref_list.insert(i, i)
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


@pytest.mark.parametrize("existing,inserts", cases, ids=[f"existing={existing + 1}-{inserts=}" for existing, inserts in cases])
def test_list_insert_existing_same(tmpdir, existing, inserts) -> None:
    ref_list = [-1 + -i for i in range(existing + 1)]
    file = "test.py"
    content = f"""
symbol = {ref_list}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        for i in range(inserts):
            symbol_list.insert(1, i)
            ref_list.insert(1, i)
    assert (
        file.content
        == f"""
symbol = {ref_list}
"""
    )


def test_list_empty(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = []
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        assert len(symbol_list) == 0
        symbol_list.append("a")
        symbol_list.append("c")
    # language=python
    assert (
        file.content
        == """
symbol = [a, c]
"""
    )


def test_list_remove_insert(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = ["a"]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        symbol_list.append("a")
        del symbol_list[0]
        symbol_list.append("c")
    # language=python
    assert (
        file.content
        == """
symbol = [a, c]
"""
    )


def test_list_edit(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = ["a"]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        symbol_list[0].edit("b")
    # language=python
    assert (
        file.content
        == """
symbol = [b]
"""
    )


def test_list_clear(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = [a, b, c]
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_list: List = symbol.value
        symbol_list.clear()
    # language=python
    assert (
        file.content
        == """
symbol = []
"""
    )
