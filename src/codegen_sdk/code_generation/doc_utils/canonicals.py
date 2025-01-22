import textwrap

from codegen_sdk.code_generation.doc_utils.utils import (
    format_python_codeblock,
)
from codegen_sdk.code_generation.enums import DocumentationDecorators
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.python.class_definition import PyClass


def get_canonical_codemod_classes(codebase: Codebase, language: ProgrammingLanguage) -> dict[str, PyClass]:
    classes = {}
    target_decorator = DocumentationDecorators.CODEMOD.value
    for cls in codebase.classes:
        if target_decorator in [decorator.name for decorator in cls.decorators]:
            if cls.get_attribute("language"):
                if cls.get_attribute("language").assignment.value.source.split(".")[1] == language.value:
                    classes[cls.name] = cls
    return classes


def get_canonical_codemod_class_docstring(symbol: PyClass) -> str:
    """Returns a markdown-formatted string for a single codemod class."""
    # =====[ Docstring ]=====
    title = symbol.name
    docstring = symbol.docstring
    if docstring:
        docstring = docstring.text
    else:
        docstring = "No docstring provided."

    # =====[ Source ]=====
    exec_method = symbol.get_method("execute")
    source = "\n".join(exec_method.source.split("\n")[1:])
    source = textwrap.dedent(source)

    # =====[ Language ]=====
    language = symbol.get_attribute("language")
    if not language:
        raise AttributeError(f"Language attribute not found for {symbol.name}")
    else:
        language_name = symbol.get_attribute("language").assignment.value.source.split(".")[1]
        lang_str = f"(language: `{language_name}`)"

    return f"""
### {title} {lang_str}

{docstring}

{format_python_codeblock(source)}
"""


def get_canonical_codemod_class_mdx(symbol: PyClass) -> str:
    """Returns a markdown-formatted string for a single codemod class."""
    # =====[ Docstring ]=====
    title = symbol.name
    docstring = symbol.docstring
    if docstring:
        docstring = docstring.text
    else:
        docstring = "No docstring provided."

    # =====[ Source ]=====
    exec_method = symbol.get_method("execute")
    source = "\n".join(exec_method.source.split("\n")[1:])
    source = textwrap.dedent(source)

    # =====[ Language ]=====
    language = symbol.get_attribute("language")
    if not language:
        raise AttributeError(f"Language attribute not found for {symbol.name}")
    else:
        language_name = symbol.get_attribute("language").assignment.value.source.split(".")[1]
        lang_str = f"(language: `{language_name}`)"

    return f"""---
title: {title}
sidebarTitle: {title}
---

{docstring}

{format_python_codeblock(source)}
"""
