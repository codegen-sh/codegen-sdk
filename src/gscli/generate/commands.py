import json
import logging
import os
import re
import shutil

import click
import inflection
from termcolor import colored

from codegen.sdk.code_generation.doc_utils.canonicals import get_canonical_codemod_class_mdx, get_canonical_codemod_classes
from codegen.sdk.code_generation.doc_utils.skills import format_all_skills
from codegen.sdk.code_generation.doc_utils.utils import get_all_classes_to_document
from codegen.sdk.code_generation.mdx_docs_generation import render_mdx_for_codebase_page, render_mdx_page_for_class
from codegen.sdk.code_generation.prompts.api_docs import get_codegen_sdk_codebase
from codegen.sdk.core.codebase import PyCodebaseType
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.python import PyClass
from codegen.sdk.skills.core.utils import get_all_skills, get_guide_skills_dict
from gscli.generate.runner_imports import _generate_runner_imports
from gscli.generate.utils import LanguageType, generate_builtins_file

logger = logging.getLogger(__name__)

AUTO_GENERATED_COMMENT = "THE CODE BELOW IS AUTO GENERATED. UPDATE THE SNIPPET BY UPDATING THE SKILL"
CODE_SNIPPETS_REGEX = r"(?:```python\n(?:(?!```)[\s\S])*?\n```|<CodeGroup>(?:(?!</CodeGroup>)[\s\S])*?</CodeGroup>)"


@click.group()
def generate() -> None:
    """Commands for running auto-generate commands, currently for typestubs, imports to include in runners, and docs"""
    ...


@generate.command()
@click.argument("docs_dir", default="docs", required=False)
def docs(docs_dir: str) -> None:
    """Compile new .MDX files for the auto-generated docs pages and write them to the file system.
    To actually deploy these changes, you must commit and merge the changes into develop

    This will generate docs using the codebase locally, including any unstaged changes
    """
    docs_dir = os.path.join(os.getcwd(), docs_dir)
    generate_docs(docs_dir)


@generate.command()
@click.argument("imports_file", default="function_imports.py", required=False)
def runner_imports(imports_file: str) -> None:
    """Generate imports to include in runner execution environment"""
    _generate_runner_imports(imports_file)


@generate.command()
def typestubs() -> None:
    """Generate typestubs for the the graphsitter Codebase module
    The Codebase class and it's constituents contain methods that should not be exposed, i.e we have private methods
    and private properties that we'd like to keep internal. So the way this works is we generate the typestubs and the remove
    the "internal" symbols. For example we'll remove:
     - "_" prefixed methods and properties
     - methods with `@noapidocs` decorator
    """
    _generate_codebase_typestubs()


def _generate_codebase_typestubs() -> None:
    initial_dir = os.getcwd()

    # right now this command expects you to run it from here
    if not initial_dir.endswith("codegen/codegen-backend"):
        print(colored("Error: Must be in a directory ending with 'codegen/codegen-backend'", "red"))
        exit(1)

    out_dir = os.path.abspath(os.path.join(initial_dir, "typings"))
    frontend_typestubs_dir = os.path.abspath(os.path.join(initial_dir, os.pardir, "codegen-frontend/assets/typestubs/graphsitter"))
    if os.path.isdir(out_dir):
        # remove typings dir if it exists
        shutil.rmtree(out_dir)
    if os.path.isdir(frontend_typestubs_dir):
        # remove typings dir if it exists
        shutil.rmtree(frontend_typestubs_dir)
    # generate typestubs in codegen-frontend/assets/typestubs/graphsitter  using pyright
    os.system("uv run pyright -p . --createstub codegen.sdk.core.codebase")
    os.system("uv run pyright -p . --createstub codegen.git")
    os.system("uv run pyright -p . --createstub networkx")
    # also generate for codemod context model and all its nested models
    os.system("uv run pyright -p . --createstub app.codemod.compilation.models.context")
    os.system("uv run pyright -p . --createstub app.codemod.compilation.models.pr_options")
    os.system("uv run pyright -p . --createstub app.codemod.compilation.models.github_named_user_context")
    os.system("uv run pyright -p . --createstub app.codemod.compilation.models.pull_request_context")
    os.system("uv run pyright -p . --createstub app.codemod.compilation.models.pr_part_context")

    # TODO fix this, to remove noapidoc and hidden methods
    # right now it uses astor.to_source, which doesn't respect the generics, and breaks things
    # strip_internal_symbols(frontend_typestubs_dir)

    # Autogenerate the builtins file based on what has apidoc, we use the same logic here as we do to generate the runner imports
    generate_builtins_file(frontend_typestubs_dir + "/__builtins__.pyi", LanguageType.BOTH)
    generate_builtins_file(frontend_typestubs_dir + "/__builtins__python__.pyi", LanguageType.PYTHON)
    generate_builtins_file(frontend_typestubs_dir + "/__builtins__typescript__.pyi", LanguageType.TYPESCRIPT)

    if os.path.isdir(out_dir):
        # remove typings dir if it exists
        shutil.rmtree(out_dir)


def generate_docs(docs_dir: str) -> None:
    """Compile new .MDX files for the auto-generated docs pages and write them to the file system.
    To actually deploy these changes, you must commit and merge the changes into develop

    This will generate docs using the codebase locally, including any unstaged changes
    """
    codebase = get_codegen_sdk_codebase()
    generate_codegen_sdk_docs(docs_dir, codebase)
    # generate_canonical_codemod_docs(docs_dir, codebase)
    generate_skills_docs(docs_dir)
    generate_guides(docs_dir)


def generate_guides(docs_dir: str):
    """Updates code snippets in the guides with the latest skill implementations"""
    guide_skills = get_guide_skills_dict()
    for guide_relative_path in guide_skills:
        guide_file_path = os.path.join(docs_dir, "codebase-sdk", str(guide_relative_path) + ".mdx")

        with open(guide_file_path) as f:
            file_content = f.read()

        for skill in guide_skills[guide_relative_path]:
            # Perform the regex search and replace
            target_name = inflection.camelize(skill.name)
            pattern = get_snippet_pattern(target_name)
            replacement = f"[//]: # (--{target_name}--)\n[//]: # (--{AUTO_GENERATED_COMMENT}--)\n\n{skill.generate_snippet()}"
            file_content = re.sub(pattern, replacement, file_content, flags=re.DOTALL)

        with open(guide_file_path, "w") as f:
            f.write(file_content)


def get_snippet_pattern(target_name: str) -> str:
    pattern = rf"\[//\]: # \(--{re.escape(target_name)}--\)\s*(?:\[//\]: # \(--{re.escape(AUTO_GENERATED_COMMENT)}--\)\s*)?"
    pattern += CODE_SNIPPETS_REGEX
    return pattern


def generate_codegen_sdk_docs(docs_dir: str, codebase: PyCodebaseType) -> None:
    """Generate the docs for the codegen_sdk API and update the mint.json"""
    print(colored("Generating codegen_sdk docs", "green"))

    # Generate docs page for codebase api and write to the file system
    mdx_page = render_mdx_for_codebase_page(codebase)
    os.makedirs(os.path.join(docs_dir, "codebase-sdk"), exist_ok=True)
    file_path = os.path.join(docs_dir, "codebase-sdk", "codebase.mdx")
    with open(file_path, "w") as f:
        f.write(mdx_page)

    # Prepare the directories for the new docs
    # Delete existing documentation directories if they exist
    # So we remove generated docs for any classes which no longer exist
    python_docs_dir = os.path.join(docs_dir, "codebase-sdk", "python")
    typescript_docs_dir = os.path.join(docs_dir, "codebase-sdk", "typescript")
    core_dir = os.path.join(docs_dir, "codebase-sdk", "core")

    for dir_path in [python_docs_dir, typescript_docs_dir, core_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    os.makedirs(python_docs_dir, exist_ok=True)
    os.makedirs(typescript_docs_dir, exist_ok=True)
    os.makedirs(core_dir, exist_ok=True)

    # Generate the docs pages for core, python, and typescript classes
    classes = get_all_classes_to_document(codebase)

    # Write the generated docs to the file system, splitting between core, python, and typescript
    # keep track of where we put each one so we can update the mint.json
    python_set = set()
    typescript_set = set()
    core_set = set()
    # TODO replace this with new `get_mdx_for_class` function
    for class_name, class_obj in classes.items():
        lower_class_name = class_name.lower()
        if lower_class_name.startswith("py"):
            file_path = os.path.join(python_docs_dir, f"{class_name}.mdx")
            python_set.add(f"codebase-sdk/python/{class_name}")
        elif lower_class_name.startswith(("ts", "jsx")):
            file_path = os.path.join(typescript_docs_dir, f"{class_name}.mdx")
            typescript_set.add(f"codebase-sdk/typescript/{class_name}")
        else:
            file_path = os.path.join(core_dir, f"{class_name}.mdx")
            core_set.add(f"codebase-sdk/core/{class_name}")

        mdx_page = render_mdx_page_for_class(cls=class_obj, codebase=codebase)
        with open(file_path, "w") as f:
            f.write(mdx_page)
    print(colored("Finished writing new .mdx files", "green"))

    # Update the core, python, and typescript page sets in mint.json
    mint_file_path = os.path.join(docs_dir, "mint.json")
    with open(mint_file_path) as mint_file:
        mint_data = json.load(mint_file)

    # Find the "Codebase SDK" group where we want to add the pages
    codebase_sdk_group = next(group for group in mint_data["navigation"] if group["group"] == "GraphSitter Reference")

    # Update the pages for each language group
    for group in codebase_sdk_group["pages"]:
        if isinstance(group, dict):  # Ensure group is a dictionary
            if group["group"] == "Core":
                group["pages"] = sorted(core_set)
            elif group["group"] == "Python":
                group["pages"] = sorted(python_set)
            elif group["group"] == "Typescript":
                group["pages"] = sorted(typescript_set)

    with open(mint_file_path, "w") as mint_file:
        json.dump(mint_data, mint_file, indent=2)

    print(colored("Updated mint.json with new page sets", "green"))


def generate_skills_docs(docs_dir: str) -> None:
    """Generates docs for all skills"""
    print(colored("Generating skills docs", "green"))
    # Interim Modification: We need to refactor all skills
    skills = [skill for skill in get_all_skills() if not skill.guide]
    skills_doc = format_all_skills(skills)

    # =====[ Write the skills docs to the file system ]=====
    core_dir = os.path.join(docs_dir, "codebase-sdk", "examples")
    file_path = os.path.join(core_dir, "skills.mdx")
    print(colored(f"> Writing to {file_path}", "green"))
    open(file_path, "w").write(skills_doc)


def document_skill(skill: PyClass):
    return "skill" in [decorator.name for decorator in skill.decorators]


def filter_class(cls: PyClass):
    for method in cls.methods:
        for decorator in method.decorators:
            if decorator.name == "skill_impl" and "external=True" in decorator.source:
                return True
    return False


def generate_canonical_codemod_docs(docs_dir: str, codebase: PyCodebaseType) -> None:
    """Generates docs for all canonical codemods"""
    print(colored("Generating canonical codemod docs", "green"))

    print(colored("> Grabbing canonicals", "green"))
    classes = get_canonical_codemod_classes(codebase, language=ProgrammingLanguage.PYTHON)

    # =====[ Write the canonical docs to the file system ]=====
    examples_dir = os.path.join(docs_dir, "codebase-sdk", "examples")
    print(colored(f"> Generating docs in {examples_dir}", "green"))
    docstrings = {k: get_canonical_codemod_class_mdx(v) for k, v in classes.items()}
    for k, v in docstrings.items():
        file_path = os.path.join(examples_dir, f"{k}.mdx")
        with open(file_path, "w") as f:
            f.write(v)

    print(colored("> Writing to disk", "green"))


if __name__ == "__main__":
    generate_skills_docs("docs")
