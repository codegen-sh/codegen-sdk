from codegen_sdk.codebase.factory.get_session import get_codebase_graph_session
from codegen_sdk.enums import ProgrammingLanguage


def test_file_get_import_string_no_params(tmpdir) -> None:
    content = """
age: int = 25;
"""
    with get_codebase_graph_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={"test.py": content}) as G:
        file = G.get_file("test.py")

        file_import_string = file.get_import_string()
        assert file_import_string == "from . import test"
