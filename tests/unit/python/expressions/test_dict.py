from itertools import product

import pytest

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.symbol_groups.dict import Dict


def test_dict_basic(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {a: 1, b: 2, c: 3}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for child in symbol_dict:
            assert child
        assert symbol_dict["a"] == "1"
        assert symbol_dict["b"] == "2"
        assert symbol_dict["c"] == "3"
        del symbol_dict["c"]
        symbol_dict["d"] = "4"
    # language=python
    assert (
        file.content
        == """
symbol = {a: 1, b: 2, d: 4}
"""
    )


def test_dict_multiline(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {
    a: 1,
    b: 2,
    c: 3,
}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for child in symbol_dict:
            assert child
        assert symbol_dict["a"] == "1"
        assert symbol_dict["b"] == "2"
        assert symbol_dict["c"] == "3"
        del symbol_dict["c"]
        symbol_dict["d"] = "4"
        symbol_dict["e"] = "5"
    # language=python
    assert (
        file.content
        == """
symbol = {
    a: 1,
    b: 2,
    d: 4,
    e: 5,
}
"""
    )


def test_dict_insert(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {a: 1, b: 2, c: 3}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        symbol_dict["d"] = "4"
    # language=python
    assert (
        file.content
        == """
symbol = {a: 1, b: 2, c: 3, d: 4}
"""
    )


cases = list(product(range(2), repeat=2))


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_dict_interleaved(tmpdir, removes, inserts) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(removes)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(max(inserts, removes)):
            if i < inserts:
                ref_dict[i] = i**2
                symbol_dict[i] = i**2
            if i < removes:
                del ref_dict[-1 - i]
                del symbol_dict[-1 - i]
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_dict_removes_first(tmpdir, removes, inserts) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(removes)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(removes):
            del ref_dict[-1 - i]
            del symbol_dict[-1 - i]
        for i in range(inserts):
            ref_dict[i] = i**2
            symbol_dict[i] = i**2
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


@pytest.mark.parametrize("removes,inserts", cases, ids=[f"{removes=}-{inserts=}" for removes, inserts in cases])
def test_dict_inserts_first(tmpdir, removes, inserts) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(removes)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(inserts):
            ref_dict[i] = i**2
            symbol_dict[i] = i**2
        for i in range(removes):
            del ref_dict[-1 - i]
            del symbol_dict[-1 - i]
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


@pytest.mark.parametrize("existing,inserts", cases, ids=[f"{existing=}-{inserts=}" for existing, inserts in cases])
def test_dict_append_existing(tmpdir, existing, inserts) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(existing)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(inserts):
            ref_dict[i] = i**2
            symbol_dict[i] = i**2
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


@pytest.mark.parametrize("existing", list(range(4)), ids=[f"existing={existing}" for existing in range(4)])
def test_dict_set_existing(tmpdir, existing) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(existing)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(existing):
            ref_dict[i] = i**2
            symbol_dict[i] = i**2
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


@pytest.mark.parametrize("existing,inserts", cases, ids=[f"existing={existing + 1}-{inserts=}" for existing, inserts in cases])
def test_dict_set_existing_same(tmpdir, existing, inserts) -> None:
    ref_dict = {-1 + -i: -(i**2) for i in range(existing)}
    file = "test.py"
    content = f"""
symbol = {ref_dict}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)
        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        for i in range(inserts):
            symbol_dict[1] = i
            ref_dict[1] = i
    assert (
        file.content
        == f"""
symbol = {ref_dict}
"""
    )


def test_dict_empty(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        assert len(symbol_dict) == 0
        symbol_dict["a"] = 0
        symbol_dict["c"] = 1
    # language=python
    assert (
        file.content
        == """
symbol = {a: 0, c: 1}
"""
    )


def test_dict_remove_insert(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {a: 1}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        symbol_dict["b"] = 1
        del symbol_dict["a"]
        symbol_dict["c"] = 2
    # language=python
    assert (
        file.content
        == """
symbol = {b: 1, c: 2}
"""
    )


def test_dict_edit(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {a: 0}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        symbol_dict["a"] = 1
    # language=python
    assert (
        file.content
        == """
symbol = {a: 1}
"""
    )


def test_dict_clear(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
symbol = {a: 1, b: 2, c: 3}
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        symbol_dict: Dict = symbol.value
        symbol_dict.clear()
    # language=python
    assert (
        file.content
        == """
symbol = {}
"""
    )
