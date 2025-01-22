from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.class_definition import Class
from graph_sitter.core.detached_symbols.function_call import FunctionCall
from graph_sitter.enums import ProgrammingLanguage


def test_class_definition_parent_class_names_single(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    FILE_CONTENT = """
class Point:
    def __init__(self):
        pass

p = Point()
"""
    with get_codebase_session(
        tmpdir=tmpdir,
        programming_language=ProgrammingLanguage.PYTHON,
        files={FILENAME: FILE_CONTENT.strip()},
    ) as codebase:
        file = codebase.get_file(FILENAME)
        point: Class = file.get_symbol("Point")
        p = file.get_symbol("p")
        call: FunctionCall = p.value
        assert call.function_definition == point.constructor
        assert point.constructor.symbol_usages == [p]
        assert len(point.constructor.usages) == 1
