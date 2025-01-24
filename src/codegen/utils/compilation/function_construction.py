from __future__ import annotations

import logging
import re

from codegen.utils.compilation.function_imports import get_generated_imports

logger = logging.getLogger(__name__)


def create_function_str_from_codeblock(codeblock: str, func_name: str) -> str:
    """Creates a function string from a codeblock."""
    # =====[ Make an `execute` function string w/ imports ]=====
    func_str = wrap_codeblock_in_function(codeblock, func_name)

    # =====[ Add imports to the top ]=====
    func_str = get_imports_string().format(func_str=func_str)
    return func_str


def wrap_codeblock_in_function(codeblock: str, func_name: str) -> str:
    """Wrap a codeblock in a function with the specified name.

    Args:
        codeblock (str): The code to be wrapped in a function.
        func_name (str): The name to give the wrapping function.

    Note:
        Skip wrapping if a function with the specified name already exists in the codeblock.
    """
    if re.search(rf"\bdef\s+{func_name}\s*\(", codeblock):
        logger.info(f"Codeblock already has a function named {func_name}. Skipping wrap.")
        return codeblock

    # If not function func_name does not already exist, create a new function with the codeblock inside
    user_code = indent_user_code(codeblock)
    codeblock = f"""
def {func_name}(codebase: Codebase, pr_options: PROptions | None = None, pr = None, **kwargs):
    print = codebase.log
{user_code}
    """
    return codeblock


def indent_user_code(codeblock: str) -> str:
    return "\n".join(f"    {line}" for line in codeblock.strip().split("\n"))


def get_imports_string():
    """Gets imports marked with apidoc decorators. This list is autogenerated by generate_runner_imports"""
    imports_str = get_generated_imports()

    func_str_template = """

{func_str}
"""
    return imports_str + func_str_template
