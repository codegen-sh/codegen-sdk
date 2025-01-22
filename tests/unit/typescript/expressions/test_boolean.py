from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.expressions.binary_expression import BinaryExpression
from graph_sitter.core.expressions.boolean import Boolean
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.typescript.assignment import TSAssignment


def test_boolean_parse(tmpdir):
    # language=typescript
    content = """
const a = true;
const b = false;
const c = true;
const d = a || b || false || c;
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.ts": content}, programming_language=ProgrammingLanguage.TYPESCRIPT) as codebase:
        file = codebase.get_file("test.ts")
        a = file.get_global_var("a")
        b = file.get_global_var("b")
        d = file.get_global_var("d")

        assert a.value
        assert not b.value
        assert isinstance(a.value, Boolean)
        assert isinstance(b.value, Boolean)
        assert isinstance(d.value, BinaryExpression)
        # TODO: FIX THIS, should all resolve to Boolean types (CG-9489)
        assert [type(e.resolved_value) for e in d.value.elements] == [Boolean, TSAssignment, Boolean, Boolean]
