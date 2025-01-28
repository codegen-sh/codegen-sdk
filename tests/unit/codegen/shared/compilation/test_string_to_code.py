from unittest.mock import MagicMock, patch

import pytest

from codegen.git.models.pr_options import PROptions
from codegen.shared.compilation.string_to_code import create_execute_function_from_codeblock
from codegen.shared.exceptions.compilation import DangerousUserCodeException, InvalidUserCodeException
from codegen.shared.exceptions.control_flow import StopCodemodException


def test_syntax_error_raises():
    codeblock = """
print "syntax error"
"""
    with pytest.raises(InvalidUserCodeException) as exc_info:
        create_execute_function_from_codeblock(codeblock=codeblock)
    assert exc_info
    error_msg = str(exc_info.value)
    assert "SyntaxError" in error_msg
    assert 'print "syntax error"' in error_msg


def test_print_os_environ_raises():
    codeblock = """
print(os.environ["ENV"])
"""
    with pytest.raises(DangerousUserCodeException):
        create_execute_function_from_codeblock(codeblock=codeblock)


def test_print_calls_codebase_log():
    """Test print is monkey patched to call codebase.log"""
    codeblock = """
print("actually codebase.log")
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock)
    mock_log = MagicMock()
    func(codebase=MagicMock(log=mock_log), pr_options=PROptions())
    assert mock_log.call_count == 1
    assert mock_log.call_args_list[0][0][0] == "actually codebase.log"


def test_set_custom_scope_does_not_raise():
    """Test if the custom scope is set and the codeblock uses a var defined in the scope, it does not raise a NameError."""
    codeblock = """
print(local_a)
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock, custom_scope={"local_a": "this is local_a"})
    mock_log = MagicMock()
    func(codebase=MagicMock(log=mock_log), pr_options=PROptions())
    assert mock_log.call_count == 1
    assert mock_log.call_args_list[0][0][0] == "this is local_a"


@patch("codegen.shared.compilation.string_to_code.logger")
def test_stop_codemod_execution_logs_and_raises(mock_logger):
    codeblock = """
local_a = "this is local_a"
raise StopCodemodException("test exception")
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock)
    with pytest.raises(StopCodemodException):
        func(codebase=MagicMock(), pr_options=PROptions())
    mock_logger.info.call_count == 2
    mock_logger.info.call_args_list[1][0][0] == "Stopping codemod due to StopCodemodException: test exception"


def test_references_import_from_generated_imports_does_not_raise():
    codeblock = """
print(os.getcwd()) # test external import
print(MessageType.GITHUB) # test gs private import
print(Export.__name__) # test gs public import
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock)
    mock_log = MagicMock()
    func(codebase=MagicMock(log=mock_log), pr_options=PROptions())
    assert mock_log.call_count == 3


def test_references_import_not_in_generated_imports_raises_runtime_error():
    codeblock = """
print(Chainable.__name__)
"""
    with pytest.raises(RuntimeError) as exc_info:
        func = create_execute_function_from_codeblock(codeblock=codeblock)
        func(codebase=MagicMock(), pr_options=PROptions())
    assert exc_info
    error_msg = str(exc_info.value)
    assert "NameError: name 'Chainable' is not defined." in error_msg
    assert "> 1:     print(Chainable.__name__)" in error_msg


def test_error_during_execution_raises_runtime_error():
    codeblock = """
print(var_that_does_not_exist)
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock)
    with pytest.raises(RuntimeError) as exc_info:
        func(codebase=MagicMock(), pr_options=PROptions())
    assert exc_info
    assert exc_info.typename == "RuntimeError"
    error_msg = str(exc_info.value)
    assert "NameError: name 'var_that_does_not_exist' is not defined" in error_msg
    assert "> 1:     print(var_that_does_not_exist)" in error_msg


@pytest.mark.xfail(reason="TODO(CG-9581): fix codeblocks with return statements")
def test_return_statement_still_returns_locals():
    """Test if there is a return statement in a customer code block, the function should still return the locals"""
    codeblock = """
local_a = "this is local_a"
return "this is a return statement"
"""
    func = create_execute_function_from_codeblock(codeblock=codeblock)
    res = func(codebase=MagicMock(), pr_options=PROptions())
    assert isinstance(res, dict)
    assert res == {"local_a": "this is local_a"}
