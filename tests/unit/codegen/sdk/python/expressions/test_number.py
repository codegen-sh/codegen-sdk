from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.expressions.binary_expression import BinaryExpression
from codegen.sdk.core.expressions.number import Number


def test_number_parse(tmpdir) -> None:
    # language=python
    content = """
a = 1
b = 2
c = 3
d = a + 5 / b * c
    """
    with get_codebase_session(tmpdir=tmpdir, files={"test.py": content}) as codebase:
        file = codebase.get_file("test.py")
        a = file.get_global_var("a")
        b = file.get_global_var("b")
        c = file.get_global_var("c")
        d = file.get_global_var("d")

        assert a.value == "1"
        assert b.value == "2"
        assert c.value == "3"
        assert d.value == "a + 5 / b * c"
        assert isinstance(a.value, Number)
        assert isinstance(b.value, Number)
        assert isinstance(c.value, Number)
        assert isinstance(d.value, BinaryExpression)
        assert [type(e.resolved_value) for e in d.value.elements] == [Number, Number, Number, Number]
        assert [e.resolved_value.source for e in d.value.elements] == ["1", "5", "2", "3"]
