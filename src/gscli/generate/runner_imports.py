from itertools import chain

from termcolor import colored

from codegen_sdk.code_generation.current_code_codebase import get_documented_objects

EXTERNAL_IMPORTS = """
import os
import re
from pathlib import Path
import networkx as nx
import plotly
""".strip()
CODEGEN_IMPORTS = """
from app.codemod.compilation.models.context import CodemodContext
from app.codemod.compilation.models.github_named_user_context import GithubNamedUserContext
from app.codemod.compilation.models.pr_part_context import PRPartContext
from app.codemod.compilation.models.pull_request_context import PullRequestContext
"""
# TODO: these should also be made public (i.e. included in the docs site)
GS_PRIVATE_IMPORTS = """
from codegen_sdk.codebase.control_flow import StopCodemodException
""".strip()

IMPORT_STRING_TEMPLATE = """
# External imports
{external_imports}

# GraphSitter imports (private)
{codegen_imports}
{gs_private_imports}

# GraphSitter imports (public)
{gs_public_imports}
""".strip()

IMPORT_FILE_TEMPLATE = '''
# This file is auto-generated, do not modify manually. Edit this in codegen-backend/cli/generate/runner_imports.py.
def get_generated_imports():
    return """
{import_str}
"""
'''.strip()


def get_runner_imports(include_codegen=True, include_private_imports: bool = True) -> str:
    # get the imports from the apidoc, py_apidoc, and ts_apidoc
    gs_objects = get_documented_objects()
    gs_public_objects = list(chain(gs_objects["apidoc"], gs_objects["py_apidoc"], gs_objects["ts_apidoc"]))
    gs_public_imports = {f"from {obj.module} import {obj.name}" for obj in gs_public_objects}

    # construct import string with all imports
    ret = IMPORT_STRING_TEMPLATE.format(
        codegen_imports=CODEGEN_IMPORTS if include_codegen else "",
        external_imports=EXTERNAL_IMPORTS,
        gs_private_imports=GS_PRIVATE_IMPORTS if include_private_imports else "",
        gs_public_imports="\n".join(sorted(gs_public_imports)),
    )
    return ret


EXPORT_TEMPLATE = """
__all__ = [
    "__version__",
    "__version_tuple__",
    "StopCodemodException",
{modules}
]
""".strip()


def generate_exported_modules() -> str:
    gs_objects = get_documented_objects()
    gs_public_objects = list(chain(gs_objects["apidoc"], gs_objects["py_apidoc"], gs_objects["ts_apidoc"]))
    return EXPORT_TEMPLATE.format(modules=",\n".join(dict.fromkeys('    "' + obj.name + '"' for obj in sorted(gs_public_objects, key=lambda x: x.name))))


def _generate_runner_imports(imports_file: str) -> None:
    print(colored(f"Generating runner imports string in {imports_file}", "green"))

    import_str = get_runner_imports()
    # write the imports to the file
    with open(imports_file, "w") as f:
        f.write(IMPORT_FILE_TEMPLATE.format(import_str=import_str))
