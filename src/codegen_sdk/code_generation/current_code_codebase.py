# TODO: move out of graph sitter, useful for other projects
import importlib
import logging
from pathlib import Path
from typing import TypedDict

from codegen_git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen_git.schemas.repo_config import BaseRepoConfig
from codegen_sdk.codebase.config import CodebaseConfig, DefaultConfig, ProjectConfig
from codegen_sdk.core.codebase import Codebase, CodebaseType
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.writer_decorators import DocumentedObject, apidoc_objects, no_apidoc_objects, py_apidoc_objects, ts_apidoc_objects

logger = logging.getLogger(__name__)


def get_graphsitter_repo_path() -> str:
    """Points to base directory of the Codegen repo (.git) that is currently running"""
    import codegen_sdk

    filepath = codegen_sdk.__file__
    codegen_base_dir = filepath.replace("/codegen_sdk/__init__.py", "")
    codegen_base_dir = codegen_base_dir.replace("/src", "")
    return codegen_base_dir


def get_codegen_codebase_base_path() -> str:
    import codegen_sdk

    filepath = codegen_sdk.__file__
    codegen_base_dir = filepath.replace("/codegen_sdk/__init__.py", "")
    return "src" if "src" in codegen_base_dir else ""


def get_current_code_codebase(config: CodebaseConfig = DefaultConfig, subdirectories: list[str] | None = None) -> CodebaseType:
    """Returns a Codebase for the code that is *currently running* (i.e. the Codegen repo)"""
    codegen_repo_path = get_graphsitter_repo_path()
    logger.info(f"Creating codebase from repo at: {codegen_repo_path} with base_path {get_codegen_codebase_base_path()}")
    op = LocalRepoOperator(repo_path=codegen_repo_path, default_branch="develop", bot_commit=False, repo_config=BaseRepoConfig(respect_gitignore=False))
    config = config.model_copy(update={"base_path": get_codegen_codebase_base_path()})
    projects = [ProjectConfig(repo_operator=op, programming_language=ProgrammingLanguage.PYTHON, subdirectories=subdirectories, base_path=get_codegen_codebase_base_path())]
    codebase = Codebase(projects=projects, config=config)
    return codebase


def import_all_codegen_sdk_modules():
    # for file in codegen_sdk:

    codegen_sdk_DIR = Path(get_graphsitter_repo_path())
    if base := get_codegen_codebase_base_path():
        codegen_sdk_DIR /= base
    codegen_sdk_DIR /= "codegen_sdk"
    for file in codegen_sdk_DIR.rglob("*.py"):
        relative_path = file.relative_to(codegen_sdk_DIR)
        # ignore braintrust_evaluator because it runs stuff on import
        if "__init__" in file.name or "braintrust_evaluator" in file.name:
            continue
        module_name = "codegen_sdk." + str(relative_path).replace("/", ".").removesuffix(".py")
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Error importing {module_name}: {e}")


class DocumentedObjects(TypedDict):
    apidoc: list[DocumentedObject]
    ts_apidoc: list[DocumentedObject]
    py_apidoc: list[DocumentedObject]
    no_apidoc: list[DocumentedObject]


def get_documented_objects() -> DocumentedObjects:
    """Get all the objects decorated with apidoc, py_apidoc, ts_apidoc, and no_apidoc decorators,
    by importing all codegen_sdk modules and keeping track of decorated objects at import time using
    the respective decorators
    """
    import_all_codegen_sdk_modules()
    from codegen_sdk.core.codebase import CodebaseType, PyCodebaseType, TSCodebaseType

    if PyCodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="PyCodebaseType", module="codegen_sdk.core.codebase", object=PyCodebaseType))
    if TSCodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="TSCodebaseType", module="codegen_sdk.core.codebase", object=TSCodebaseType))
    if CodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="CodebaseType", module="codegen_sdk.core.codebase", object=CodebaseType))
    return {"apidoc": apidoc_objects, "py_apidoc": py_apidoc_objects, "ts_apidoc": ts_apidoc_objects, "no_apidoc": no_apidoc_objects}
