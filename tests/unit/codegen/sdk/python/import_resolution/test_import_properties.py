from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_module_name(tmpdir) -> None:
    # language=python
    content = """
import foo
from bar import baz
from .local import thing
from ..parent import other
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imports = file.imports

        # Test regular import
        assert imports[0].module_name == "foo"
        # Test from import
        assert imports[1].module_name == "bar"
        # Test relative import
        assert imports[2].module_name == ".local"
        # Test parent relative import
        assert imports[3].module_name == "..parent"


def test_is_from_import(tmpdir) -> None:
    # language=python
    content = """
import module1
import module2 as alias
from module3 import symbol
from .module4 import symbol
from module5 import (a, b, c)
from module6 import *
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imports = file.imports

        # Regular imports should return False
        assert not imports[0].is_from_import()
        assert not imports[1].is_from_import()

        # From imports should return True
        assert imports[2].is_from_import()
        assert imports[3].is_from_import()
        assert imports[4].is_from_import()
        assert imports[5].is_from_import()


def test_is_future_import(tmpdir) -> None:
    # language=python
    content = """
from __future__ import annotations
import module1
from module2 import thing
from __future__ import division
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        imports = file.imports

        # Only __future__ imports should return True
        assert imports[0].is_future_import
        assert not imports[1].is_future_import
        assert not imports[2].is_future_import
        assert imports[3].is_future_import
