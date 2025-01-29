import pytest

from codegen.shared.compilation.function_compilation import safe_compile_function_string
from codegen.shared.exceptions.compilation import InvalidUserCodeException


def test_valid_func_str_should_not_raise() -> None:
    func_str = """
from codegen.sdk.core.codebase import Codebase

def execute(codebase: Codebase):
    print(len(codebase.files))
"""
    try:
        safe_compile_function_string(custom_scope={}, func_name="execute", func_str=func_str)
    except InvalidUserCodeException:
        pytest.fail("Unexpected InvalidUserCodeException raised")


def test_valid_func_str_with_nested_should_not_raise() -> None:
    func_str = """
from codegen.sdk.core.codebase import Codebase

def execute(codebase: Codebase):
    def nested():
        return "I'm nested!"
    print("calling nested")
    nested()
"""
    try:
        safe_compile_function_string(custom_scope={}, func_name="execute", func_str=func_str)
    except InvalidUserCodeException:
        pytest.fail("Unexpected InvalidUserCodeException raised")


def test_compile_syntax_error_indent_error_raises() -> None:
    func_str = """
def execute(codebase: Codebase):
a = 1
    print(a)
"""
    with pytest.raises(InvalidUserCodeException) as exc_info:
        safe_compile_function_string(custom_scope={}, func_name="execute", func_str=func_str)
    assert exc_info
    error_msg = str(exc_info.value)
    assert "IndentationError" in error_msg  # an example of a SyntaxError
    assert "> 3: a = 1" in error_msg


def test_compile_syntax_error_raises() -> None:
    func_str = """
def execute(codebase: Codebase):
    print "syntax error"
"""

    with pytest.raises(InvalidUserCodeException) as exc_info:
        safe_compile_function_string(custom_scope={}, func_str=func_str, func_name="execute")
    assert exc_info
    error_msg = str(exc_info.value)
    assert "SyntaxError" in error_msg
    assert '> 3:     print "syntax error"' in error_msg


def test_compile_non_syntax_error_unicode_error_raises() -> None:
    func_str = """
def execute(codebase: Codebase):
    print("hello")\udcff
"""

    SyntaxError()
    with pytest.raises(InvalidUserCodeException) as exc_info:
        safe_compile_function_string(custom_scope={}, func_str=func_str, func_name="execute")
    assert exc_info
    error_msg = str(exc_info.value)
    assert "UnicodeEncodeError" in error_msg
    # TODO: why is this missing the error context lines?
    # TODO: also the error line number is the line in the source code not in the func_str
    assert "'utf-8' codec can't encode character '\\udcff'" in error_msg


def test_exec_error_non_syntax_error_zero_division_raises() -> None:
    """This is to test that we're handling errors (ex: ZeroDivisionError) that are raised during `exec` properly.

    NOTE: this case wouldn't happen with an actual func_str from create_function_str_from_codeblock b/c the func_str would just take in a codebase.
    """
    func_str = """
def execute(codebase: Codebase, exec_error: int = 1/0):
    print("zero division error")
"""
    with pytest.raises(InvalidUserCodeException) as exc_info:
        safe_compile_function_string(custom_scope={}, func_str=func_str, func_name="execute")
    assert exc_info
    error_msg = str(exc_info.value)
    assert "ZeroDivisionError" in error_msg
    assert "> 2: def execute(codebase: Codebase, exec_error: int = 1/0):" in error_msg


def test_exec_error_non_syntax_error_name_error_raises() -> None:
    """This is to test that we're handling errors (ex: NameError) that are raised during `exec` properly.

    NOTE: this case wouldn't happen with an actual func_str from create_function_str_from_codeblock b/c the func_str would not have any patches.
    """
    func_str = """
@patch("foo", return_value="bar")
def execute(codebase: Codebase):
    print("zero division error")
"""
    with pytest.raises(InvalidUserCodeException) as exc_info:
        safe_compile_function_string(custom_scope={}, func_str=func_str, func_name="execute")
    assert exc_info
    error_msg = str(exc_info.value)
    assert "NameError" in error_msg
    assert '> 2: @patch("foo", return_value="bar")' in error_msg


def test_func_str_uses_custom_scope_var_does_not_raise() -> None:
    """This tests if a func_str references a var that is included in custom scope, it will not raise a NameError.
    This is to test the case when a group of codemods is run and a later one relies on a local defined in a previous one.
    """
    func_str = """
print(local_a)
"""
    try:
        safe_compile_function_string(custom_scope={"local_a": "this is local_a"}, func_str=func_str, func_name="execute")
    except InvalidUserCodeException:
        pytest.fail("Unexpected InvalidPythonCodeException raised")
