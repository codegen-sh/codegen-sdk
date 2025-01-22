import textwrap

import inflection
from typing_extensions import deprecated

from codegen_sdk.codemod import Codemod3
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.enums import ProgrammingLanguage
from codegen_sdk.python import PyClass
from codegen_sdk.python.function import PyFunction
from codegen_sdk.skills.core.skill import Skill
from codegen_sdk.skills.core.skill_implementation import SkillImplementation
from codegen_sdk.skills.core.utils import get_all_evaluation_skills


def remove_leading_tab_or_spaces(text: str) -> str:
    """Removes the leading tab or four spaces from the first line of a string."""
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        if line.startswith("\t"):
            out_lines.append(line[1:])
        elif line.startswith("    "):
            out_lines.append(line[4:])
    return "\n".join(out_lines)


def format_skill_function_mdx(skill: PyFunction, name: str | None = None, dedent: bool = False) -> str:
    """Returns a .mdx for a skill implementation"""
    if name is None:
        name = skill.name
    docstring = skill.docstring
    docstring = skill.docstring.source if docstring else ""
    raw_docstring = docstring.replace('"""', "")
    raw_source = skill.code_block.source.replace(docstring, "")
    raw_source = remove_leading_tab_or_spaces(raw_source)
    if dedent:
        raw_source = textwrap.dedent(raw_source)
    return f"""## {name}
{raw_docstring}
```python
{raw_source}
```"""


def format_skill_code_group_mdx(skill: PyFunction, name: str | None = None, dedent: bool = False) -> str:
    """Returns a .mdx for a skill code group. See https://mintlify.com/docs/content/components/code-groups"""
    if name is None:
        name = skill.name
    if skill is None:
        raise ValueError(f"Skill is None. name: {name}")
    docstring = skill.docstring
    docstring = skill.docstring.source if docstring else ""
    raw_docstring = docstring.replace('"""', "")
    raw_source = skill.code_block.source.replace(docstring, "")
    raw_source = remove_leading_tab_or_spaces(raw_source)
    if dedent:
        raw_source = textwrap.dedent(raw_source)
    return raw_source


def get_skill_function(skill: PyClass, skill_func_name: str) -> PyFunction:
    python_skill_func = skill.get_method(skill_func_name)
    if python_skill_func.code_block.source.strip() == "...":
        if skill.get_method("skill_func").code_block.source.strip() != "...":
            python_skill_func = skill.get_method("skill_func")
        elif skill.get_method("execute").code_block.source.strip() != "...":
            python_skill_func = skill.get_method("execute")
    return python_skill_func


def format_skill_class_mdx(skill: PyClass) -> str:
    """Returns a .mdx for a skill"""
    name = inflection.underscore(skill.name)
    docstring = skill.docstring
    docstring = skill.docstring.source if docstring else ""
    raw_docstring = docstring.replace('"""', "")
    raw_source = skill.code_block.source.replace(docstring, "")
    raw_source = remove_leading_tab_or_spaces(raw_source)
    raw_source = textwrap.dedent(raw_source)

    python_skill_func = get_skill_function(skill, "python_skill_func")
    typescript_skill_func = get_skill_function(skill, "typescript_skill_func")

    return f"""
## {name}

{raw_docstring}

<CodeGroup>

```python python
{format_skill_code_group_mdx(python_skill_func, name=f"{name}_python", dedent=True)}
```

```python typescript
{format_skill_code_group_mdx(typescript_skill_func, name=f"{name}_typescript", dedent=True)}
```
</CodeGroup>
"""


def format_all_skills(skill_classes: list[Skill]) -> str:
    """Returns a string of .mdx for all skills"""
    # Step 1: Sort all skills by name so they appear in alpha order in the docs
    sorted_skills = sorted(skill_classes, key=lambda x: x.name)
    formatted_skills = []

    # Step 2: Format each skill into an .mdx compatible string
    for skill in sorted_skills:
        if issubclass(skill, Codemod3):
            continue
        sk_inst = skill
        formatted_skills.append(sk_inst.generate_snippet(skill_doc=True))

    # Step 3: Render full .mdx skills page
    return f"""---
title: "Skills"
sidebarTitle: "Skills"
description: "Common GraphSitter code snippets"
---

{"\n\n".join(formatted_skills)}
"""


@deprecated("Generating skills docs no longer requires <codebase>")
def get_skill_functions(codebase: Codebase, language: ProgrammingLanguage) -> list[PyFunction]:
    return [c for c in codebase.functions if any(["@skill_impl" in d.source for d in c.decorators])]


@deprecated("Generating skills docs no longer requires <codebase>")
def get_skill_classes(codebase: Codebase, language: ProgrammingLanguage) -> list[PyClass]:
    return [c for c in codebase.classes if any(["@skill" in d.source for d in c.decorators])]


@deprecated("Generating skills docs no longer requires <codebase>")
def get_skills_docstring(codebase: Codebase, language: ProgrammingLanguage) -> str:
    """Idea here is to perform some sort of RAG and return the skills in a markdown format"""
    skill_functions = get_skill_functions(codebase, language)
    skill_classes = get_skill_classes(codebase, language)
    skillz = format_all_skills(skill_functions, skill_classes)
    return f"""### Skills

{skillz}
"""


def get_formatted_skills() -> str:
    """Format a list of SkillImplementations to mdx. Used to avoid reloading <codebase()>"""
    skills: list[SkillImplementation] = get_all_evaluation_skills()
    formatted_skills = []
    for skill in skills:
        skill_str = f"""### {skill.name}
{skill.doc}
```python
{skill.function_body}
```"""
        formatted_skills.append(skill_str)

    return f"""## Skills
---
title: "Skills"
sidebarTitle: "Skills"
description: "Common GraphSitter code snippets"
---

{"\n\n".join(formatted_skills)}
"""
