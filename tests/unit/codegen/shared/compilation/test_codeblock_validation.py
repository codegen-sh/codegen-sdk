import pytest

from codegen.shared.compilation.codeblock_validation import check_for_dangerous_operations
from codegen.shared.exceptions.compilation import DangerousUserCodeException


def test_no_dangerous_operations():
    codeblock = """
print("not dangerous")
"""
    try:
        check_for_dangerous_operations(codeblock)
    except DangerousUserCodeException:
        pytest.fail("Unexpected DangerousPythonCodeError raised")


def test_dangerous_operations():
    codeblock = """
print(os.environ["ENV"])
"""
    with pytest.raises(DangerousUserCodeException):
        check_for_dangerous_operations(codeblock)
