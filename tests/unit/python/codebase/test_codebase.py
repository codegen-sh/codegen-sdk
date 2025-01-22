from graph_sitter.codebase.factory.get_session import get_codebase_session


def test_codebase_symbols(tmpdir) -> None:
    # language=python
    content = """
def top_level_func():
    return 1 + 2

class MyClass1:
    def foo(self):
        print("hello world!")
"""
    with get_codebase_session(tmpdir=tmpdir, files={"file1.py": content}) as codebase:
        assert len(list(codebase.functions)) == 1
        assert [f.name for f in codebase.functions] == ["top_level_func"]
        assert len(list(codebase.symbols)) == 2
        assert set([s.name for s in codebase.symbols]) == {"top_level_func", "MyClass1"}
