from codegen_sdk.codebase.factory.get_session import get_codebase_session


def test_import_rename_usage_with_alias(tmpdir) -> None:
    # language=python
    content1 = """
from file1 import foo1, foo2
from file2 import foo3 as f2
from file3 import bar
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1}) as codebase:
        file = codebase.get_file("file1.py")
        assert file.has_import("foo2")
        assert file.has_import("f2")
        assert file.has_import("bar")
        assert not file.has_import("foo3")
