from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_file_add_symbol_import_updates_source(tmpdir) -> None:
    # language=python
    content1 = """
import datetime

def foo():
    return datetime.datetime.now()
"""

    # language=python
    content2 = """
def bar():
    return 1
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content1, "file2.py": content2}) as codebase:
        file1 = codebase.get_file("file1.py")
        file2 = codebase.get_file("file2.py")

        file2.add_symbol_import(file1.get_symbol("foo"))

    assert "import foo" in file2.content
