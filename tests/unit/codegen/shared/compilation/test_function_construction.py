from unittest.mock import patch

from codegen.shared.compilation.function_construction import create_function_str_from_codeblock


def test_no_execute_func_wraps():
    codeblock = """
print(len(codebase.files))
"""
    func = create_function_str_from_codeblock(codeblock, func_name="execute")
    assert (
        """
def execute(codebase: Codebase, pr_options: PROptions | None = None, pr = None, **kwargs):
    print = codebase.log
    print(len(codebase.files))
"""
        in func
    )


def test_func_name_already_exists():
    codeblock = """
def execute(codebase: Codebase):
    print(len(codebase.files))
"""
    func = create_function_str_from_codeblock(codeblock, func_name="execute")
    assert codeblock in func


def test_func_name_not_execute():
    codeblock = """
print(len(codebase.files))
"""
    func = create_function_str_from_codeblock(codeblock, func_name="not_execute")
    assert (
        """
def not_execute(codebase: Codebase, pr_options: PROptions | None = None, pr = None, **kwargs):
    print = codebase.log
    print(len(codebase.files))
"""
        in func
    )


def test_function_str_includes_imports():
    codeblock = """
print(len(codebase.files))
"""
    with patch("codegen.shared.compilation.function_construction.get_generated_imports", return_value="from foo import bar"):
        func = create_function_str_from_codeblock(codeblock, func_name="execute")
    assert "from foo import bar" in func
