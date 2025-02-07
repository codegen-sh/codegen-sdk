from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ImportType


def test_parse_import_statement(tmpdir) -> None:
    # language=python
    content = """
import m1
import m2, m3, m4
import m5 as m5_alias
import m6 as m6_alias, m7, m8 as m8_alias
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 4
        assert len(file.imports) == 8
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("import m1", "m1", "m1", "m1", "m1"),
            ("import m2, m3, m4", "m2", "m2", "m2", "m2"),
            ("import m2, m3, m4", "m3", "m3", "m3", "m3"),
            ("import m2, m3, m4", "m4", "m4", "m4", "m4"),
            ("import m5 as m5_alias", "m5", "m5", "m5_alias", "m5_alias"),
            ("import m6 as m6_alias, m7, m8 as m8_alias", "m6", "m6", "m6_alias", "m6_alias"),
            ("import m6 as m6_alias, m7, m8 as m8_alias", "m7", "m7", "m7", "m7"),
            ("import m6 as m6_alias, m7, m8 as m8_alias", "m8", "m8", "m8_alias", "m8_alias"),
        ]
        assert all(imp.import_type == ImportType.MODULE for imp in file.imports)


def test_parse_import_from_statement(tmpdir) -> None:
    # language=python
    content = """
from m1 import s1
from m2 import s2, s3, s4
from m3 import s5 as s5_alias
from m4 import s6 as s6_alias, s7, s8 as s8_alias
from m5 import *
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 5
        assert len(file.imports) == 9
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("from m1 import s1", "m1", "s1", "s1", "s1"),
            ("from m2 import s2, s3, s4", "m2", "s2", "s2", "s2"),
            ("from m2 import s2, s3, s4", "m2", "s3", "s3", "s3"),
            ("from m2 import s2, s3, s4", "m2", "s4", "s4", "s4"),
            ("from m3 import s5 as s5_alias", "m3", "s5", "s5_alias", "s5_alias"),
            ("from m4 import s6 as s6_alias, s7, s8 as s8_alias", "m4", "s6", "s6_alias", "s6_alias"),
            ("from m4 import s6 as s6_alias, s7, s8 as s8_alias", "m4", "s7", "s7", "s7"),
            ("from m4 import s6 as s6_alias, s7, s8 as s8_alias", "m4", "s8", "s8_alias", "s8_alias"),
            ("from m5 import *", "m5", "m5", "m5", "m5"),
        ]
        assert all(imp.import_type == ImportType.NAMED_EXPORT for imp in file.imports[:-1])
        assert file.imports[-1].import_type == ImportType.WILDCARD


def test_parse_relative_import(tmpdir) -> None:
    # language=python
    content = """
from . import m1
from .. import m2, m3, m4
from ... import m5 as m5_alias
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 3
        assert len(file.imports) == 5
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("from . import m1", ".", "m1", "m1", "m1"),
            ("from .. import m2, m3, m4", "..", "m2", "m2", "m2"),
            ("from .. import m2, m3, m4", "..", "m3", "m3", "m3"),
            ("from .. import m2, m3, m4", "..", "m4", "m4", "m4"),
            ("from ... import m5 as m5_alias", "...", "m5", "m5_alias", "m5_alias"),
        ]
        assert all(imp.import_type == ImportType.NAMED_EXPORT for imp in file.imports)


def test_parse_dotted_module_import(tmpdir) -> None:
    # language=python
    content = """
import d1.m1
from d2.m2 import s1
from d2.m3 import d3.s1
from ..package import s2
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 4
        assert len(file.imports) == 4
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("import d1.m1", "d1.m1", "d1.m1", "d1.m1", "d1.m1"),
            ("from d2.m2 import s1", "d2.m2", "s1", "s1", "s1"),
            ("from d2.m3 import d3.s1", "d2.m3", "d3.s1", "d3.s1", "d3.s1"),
            ("from ..package import s2", "..package", "s2", "s2", "s2"),
        ]
        assert all(imp.import_type == ImportType.NAMED_EXPORT for imp in file.imports[1:])
        assert file.imports[0].import_type == ImportType.MODULE


def test_parse_future_import_statement(tmpdir) -> None:
    # language=python
    content = """
from __future__ import annotations
from __future__ import division, print_function, unicode_literals
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 2
        assert len(file.imports) == 4
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("from __future__ import annotations", "annotations", "annotations", "annotations", "annotations"),
            ("from __future__ import division, print_function, unicode_literals", "division", "division", "division", "division"),
            ("from __future__ import division, print_function, unicode_literals", "print_function", "print_function", "print_function", "print_function"),
            ("from __future__ import division, print_function, unicode_literals", "unicode_literals", "unicode_literals", "unicode_literals", "unicode_literals"),
        ]
        assert all(imp.import_type == ImportType.SIDE_EFFECT for imp in file.imports)


def test_parse_local_imports(tmpdir) -> None:
    # language=python
    content = """
import f1

def foo():
    from dir import f2
    pass

class Bar:
    from dir.f2 import s1 as s1_alias
    pass
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.import_statements) == 3
        assert len(file.imports) == 3
        assert [(imp.source, imp.module.source, imp.symbol_name.source, imp.alias.source, imp.name) for imp in file.imports] == [
            ("import f1", "f1", "f1", "f1", "f1"),
            ("from dir import f2", "dir", "f2", "f2", "f2"),
            ("from dir.f2 import s1 as s1_alias", "dir.f2", "s1", "s1_alias", "s1_alias"),
        ]
