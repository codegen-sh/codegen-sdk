import pytest

from codegen_sdk.codebase.factory.get_session import get_codebase_session


@pytest.mark.skip(reason="Not implementing AST Grep for now. Much better ways of doing this.")
def test_ast_grep(tmpdir) -> None:
    # language=python
    content = """
print("hello, world!")
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        file.ast_grep_replace(
            pattern="print($A)",
            replace="print('REPLACED')",
        )
        codebase.commit()
        assert "REPLACED" in file.source
