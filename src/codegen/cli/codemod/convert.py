from textwrap import indent


def convert_to_cli(input: str, language: str, name: str) -> str:
    codebase_type = "PyCodebaseType" if language.lower() == "python" else "TSCodebaseType"
    return f"""import codegen.cli.sdk.decorator
# from app.codemod.compilation.models.context import CodemodContext
#from app.codemod.compilation.models.pr_options import PROptions

from codegen.sdk import {codebase_type}

context: Any


@codegen.cli.sdk.decorator.function('{name}')
def run(codebase: {codebase_type}, pr_options: Any):
{indent(input, "    ")}
"""


def convert_to_ui(input: str) -> str:
    return input
