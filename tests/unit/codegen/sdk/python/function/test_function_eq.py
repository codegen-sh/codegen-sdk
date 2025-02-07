from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_function_statements_contains(tmpdir) -> None:
    # language=python
    content = """
def g(tmpdir):
    a = 1
    b = 2
    c = 3
"""
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")

        g = file.get_symbol("g")
        assert "a = 1" in g.code_block.statements
        assert "b = 2" in g.code_block.statements
        assert "c = 3" in g.code_block.statements
        assert "d = 1" not in g.code_block.statements
