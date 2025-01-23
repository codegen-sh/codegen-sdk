from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.file import SourceFile
from codegen.sdk.core.import_resolution import Import, ImportResolution


def test_import_properties_basic(tmpdir) -> None:
    # language=python
    content = """
import a
import b.c as C
from d.e import f as F
import a.b.c
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        z = file.imports
        assert len(z) == 4
        assert z[0].source == "import a"
        assert z[0].module.source == "a"
        assert z[0].symbol_name.source == "a"
        assert z[0].alias.source == "a"

        assert z[1].source == "import b.c as C"
        assert z[1].module.source == "b.c"
        assert z[1].symbol_name.source == "b.c"
        assert z[1].alias.source == "C"

        assert z[2].source == "from d.e import f as F"
        assert z[2].module.source == "d.e"
        assert z[2].symbol_name.source == "f"
        assert z[2].alias.source == "F"

        assert z[3].source == "import a.b.c"
        assert z[3].module.source == "a.b.c"
        assert z[3].symbol_name.source == "a.b.c"
        assert z[3].alias.source == "a.b.c"


def test_import_properties(tmpdir) -> None:
    # language=python
    content = """
import x
import a.b.c
from a import b
from b.c import d
from e.f import g as h
from e.f.g import (i as j, k as l, m as n)
import x.y.z.foo as foo_bar # toughie
"""

    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        # =====[ Look at the objects ]=====
        imports = file.imports
        assert len(imports) == 9
        aliases = [x.alias.source for x in imports]
        assert "x" in aliases
        assert "a.b.c" in aliases
        assert "b" in aliases
        assert "d" in aliases
        assert "h" in aliases
        assert "g" not in aliases
        assert "i" not in aliases
        assert "j" in aliases
        assert "k" not in aliases
        assert "l" in aliases
        assert "m" not in aliases
        assert "n" in aliases
        assert "foo_bar" in aliases

        # =====[ Test equality ]=====
        imports = file.imports
        assert file == file
        assert imports[0] == imports[0]
        assert imports[0] != imports[1]


def test_import_properties_multi_imports(tmpdir) -> None:
    # language=python
    content = """
import a
from a.b.c import g
from a.b.c import (
    e,
    f,
)
from a.b import (
    d,
    e as E,
    f as F
)
import a as A
"""

    # language=python
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        z = file.imports
        assert set(i.alias.source for i in file.imports) == {"a", "g", "e", "d", "E", "F", "A", "f"}
        assert len(z) > 0

        # =====[ "import a" ]=====
        assert z[0].source == "import a"

        # =====[ "from a.b.c import d" ]=====
        assert z[1].source == "from a.b.c import g"
        assert z[1].module.source == "a.b.c"
        assert z[1].symbol_name.source == "g"

        # =====[ "from a.b.c import (e, f)" ]=====
        assert (
            z[2].source
            == """from a.b.c import (
    e,
    f,
)"""
        )
        assert z[2].module.source == "a.b.c"
        assert z[2].symbol_name.source == "e"

        # =====[ "from a.b.c import (e, f)" ]=====
        assert z[3].module.source == "a.b.c"
        assert z[3].symbol_name.source == "f"
        assert (
            z[3].source
            == """from a.b.c import (
    e,
    f,
)"""
        )

        # =====[ "from a.b import (d, e as E, f as F)" ]=====
        assert (
            z[4].source
            == """from a.b import (
    d,
    e as E,
    f as F
)"""
        )
        assert z[4].module.source == "a.b"
        assert z[4].symbol_name.source == "d"
        assert z[4].alias.source == "d"
        assert (
            z[5].source
            == """from a.b import (
    d,
    e as E,
    f as F
)"""
        )
        assert z[5].module.source == "a.b"
        assert z[5].symbol_name.source == "e"
        assert z[5].alias.source == "E"
        assert (
            z[6].source
            == """from a.b import (
    d,
    e as E,
    f as F
)"""
        )
        assert z[6].module.source == "a.b"
        assert z[6].symbol_name.source == "f"
        assert z[6].alias.source == "F"

        # =====[ import a as A ]=====
        assert z[7].source == "import a as A"
        assert z[7].module.source == "a"
        assert z[7].symbol_name.source == "a"
        assert z[7].alias.source == "A"


def test_import_resolution_file_import(tmpdir: str) -> None:
    """Tests function.usages returns usages from file imports"""
    # language=python
    with get_codebase_session(
        tmpdir,
        files={
            "a/b/c/src.py": """
def update():
    pass
""",
            "consumer.py": """
from a.b.c import src as operations

def func_1():
    operations.update()
""",
        },
    ) as codebase:
        src_file: SourceFile = codebase.get_file("a/b/c/src.py")
        consumer_file: SourceFile = codebase.get_file("consumer.py")

        # =====[ Imports & Resolution ]=====
        assert len(consumer_file.imports) == 1
        src_import: Import = consumer_file.imports[0]
        src_import_resolution: ImportResolution = src_import.resolve_import()
        assert src_import_resolution
        assert src_import_resolution.from_file is src_file
        assert src_import_resolution.imports_file is True

        # =====[ Look at call-sites ]=====
        update = src_file.get_function("update")
        call_sites = update.call_sites
        assert len(call_sites) == 1
        call_site = call_sites[0]
        assert call_site.file == consumer_file


def test_import_resolution_circular(tmpdir: str) -> None:
    """Tests function.usages returns usages from file imports"""
    # language=python
    with get_codebase_session(
        tmpdir,
        files={
            "a.py": """
from b import *
def a_sym():
    pass
""",
            "b.py": """
from c import *
def b_sym():
    pass

""",
            "c.py": """
from a import *
def c_sym():
    pass

        """,
        },
    ) as codebase:
        a_file: SourceFile = codebase.get_file("a.py")
        b_file: SourceFile = codebase.get_file("b.py")
        c_file: SourceFile = codebase.get_file("c.py")
        assert "b_sym" in a_file.valid_symbol_names
        assert "c_sym" in a_file.valid_symbol_names
        assert "a_sym" in b_file.valid_symbol_names
        assert "c_sym" in b_file.valid_symbol_names
        assert "a_sym" in c_file.valid_symbol_names
        assert "b_sym" in c_file.valid_symbol_names.keys()
