import pytest

from codegen.sdk.codebase.factory.get_session import get_codebase_session


@pytest.mark.skip("TODO: @caroljung fix this once code block for file and symbols are unified")
def test_file_statements(tmpdir) -> None:
    # language=python
    content = """
import a
b()
c = 1

def d():
    return 1
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        assert len(file.code_block.statements) == 4
        assert len(file.code_block.get_statements()) == 5
