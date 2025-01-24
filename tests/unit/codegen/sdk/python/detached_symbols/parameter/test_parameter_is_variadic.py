from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.core.function import Function
from codegen.sdk.enums import ProgrammingLanguage


def test_parameter_args_is_variadic_should_return_true(tmpdir) -> None:
    filename = "test.py"
    # language=python
    file_content = """
def foo(*args):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={filename: file_content}) as codebase:
        file = codebase.get_file(filename)
        symbol: Function = file.get_symbol("foo")
        assert symbol is not None
        assert len(symbol.parameters) == 1
        assert symbol.parameters[0].is_variadic


def test_parameter_kwargs_is_variadic_should_return_true(tmpdir) -> None:
    filename = "test.py"
    # language=python
    file_content = """
def foo(**kwargs):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={filename: file_content}) as codebase:
        file = codebase.get_file(filename)
        symbol: Function = file.get_symbol("foo")
        assert symbol is not None
        assert len(symbol.parameters) == 1
        assert symbol.parameters[0].is_variadic


def test_parameter_is_variadic_should_return_false(tmpdir) -> None:
    filename = "test.py"
    # language=python
    file_content = """
def foo(args):
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={filename: file_content}) as codebase:
        file = codebase.get_file(filename)
        symbol: Function = file.get_symbol("foo")
        assert symbol is not None
        assert len(symbol.parameters) == 1
        assert not symbol.parameters[0].is_variadic
