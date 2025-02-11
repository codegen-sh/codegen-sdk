from typing import TYPE_CHECKING

from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.dataclasses.usage import UsageKind

if TYPE_CHECKING:
    from codegen.sdk.core.symbol_groups.tuple import Tuple


def test_unpacking_tuple(tmpdir) -> None:
    file = "test.py"
    # language=python
    content = """
_,symbol,_ = (a, b, c)
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")

        len(symbol.usages) == 0


def test_unpacking_tuple_with_use(tmpdir) -> None:
    """Tests that unused variables that are part of unpacking are in use"""
    file = "test.py"
    # language=python
    content = """
foo,symbol,bar = (a, b, c)

test=symbol
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file(file)

        symbol = file.get_symbol("symbol")
        foo = file.get_symbol("foo")
        bar = file.get_symbol("bar")

        symbol_list: Tuple = symbol.value

        len(symbol.usages) == 1
        symbol.usages[0].kind == UsageKind.BODY

        len(foo.usages) == 1
        foo.usages[0].kind == UsageKind.ASSIGNMENT_SIBLING

        len(bar.usages) == 1
        bar.usages[0].kind == UsageKind.ASSIGNMENT_SIBLING
