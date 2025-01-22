from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.core.expressions.binary_expression import BinaryExpression
from codegen_sdk.core.expressions.boolean import Boolean
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.python.assignment import PyAssignment


def test_boolean_parse(tmpdir):
    # language=python
    content = """
a = True
b = False
c = True
d = a or b or False or c
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}, programming_language=ProgrammingLanguage.PYTHON) as codebase:
        file = codebase.get_file("test.py")
        a = file.get_global_var("a")
        b = file.get_global_var("b")
        d = file.get_global_var("d")

        assert a.value
        assert not b.value
        assert isinstance(a.value, Boolean)
        assert isinstance(b.value, Boolean)
        assert isinstance(d.value, BinaryExpression)
        # TODO: FIX THIS, should all resolve to Boolean types (CG-9489)
        assert [type(e.resolved_value) for e in d.value.elements] == [Boolean, PyAssignment, Boolean, Boolean]
