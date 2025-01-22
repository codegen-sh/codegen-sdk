import pytest

from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_import_usages_symbol_redefinition(tmpdir) -> None:
    # language=python
    content = """
from a.b.c import A

class A:
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        imports = file.imports
        assert len(imports) == 1  # make it 1 for now
        assert len(imports[0].symbol_usages) == 0


def test_import_usages_as_module(tmpdir) -> None:
    # language=python
    content = """
import a.b.c
import x.y
import d.e.f as def_dao

def f(tmpdir):
    a.b.c.d()
    x.y.z.a()
    def_dao.test()
"""

    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imp = file.imports[0]
        imp2 = file.imports[1]
        imp3 = file.imports[2]

        assert len(imp.symbol_usages) == 1
        assert len(imp2.symbol_usages) == 1
        assert len(imp3.symbol_usages) == 1


def test_import_usages_in_function(tmpdir) -> None:
    # language=python
    content = """
import d.e.f as def_dao

def f(tmpdir):
    def_dao.test()
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imp = file.imports[0]

        assert len(imp.symbol_usages) == 1


@pytest.mark.skip("Cycle detection is finicky")
def test_import_all_usages_with_import_loop(tmpdir) -> None:
    # language=python
    content1 = """
from b import y
"""
    # language=python
    content2 = """
from c import y
    """
    # language=python
    content3 = """
from a import y
"""
    with get_codebase_session(tmpdir=tmpdir, files={"a.py": content1, "b.py": content2, "c.py": content3}) as codebase:
        file = codebase.get_file("a.py")
        imp = file.imports[0]

        assert set([x.source for x in imp.symbol_usages]) == {"from b import y", "from c import y", "from a import y"}
        assert len(imp.symbol_usages) == 3
