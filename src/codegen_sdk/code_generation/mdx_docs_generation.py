import textwrap

from codegen_sdk.code_generation.doc_utils.utils import (
    filter_undocumented_methods_list,
    get_all_classes_to_document,
    get_nearest_parent_docstring,
    is_property,
    sanitize_mdx_mintlify_desscription,
)
from codegen_sdk.core.codebase import Codebase
from codegen_sdk.python.class_definition import PyClass
from codegen_sdk.python.detached_symbols.parameter import PyParameter
from codegen_sdk.python.function import PyFunction
from codegen_sdk.python.statements.attribute import PyAttribute


def render_mdx_for_codebase_page(codebase: Codebase) -> str:
    """Renders the MDX for the `Codebase` page"""
    cls = codebase.get_symbol("Codebase")

    return f"""{render_mdx_page_title(cls, icon="brain-circuit")}
{render_mdx_inheritence_section(cls, codebase)}
{render_mdx_properties_section(cls)}
{render_mdx_methods_section(cls)}
"""


def render_mdx_page_for_class(cls: PyClass, codebase: Codebase) -> str:
    """Renders the MDX for a single class"""
    return f"""{render_mdx_page_title(cls)}
{render_mdx_inheritence_section(cls, codebase)}
{render_mdx_properties_section(cls)}
{render_mdx_attributes_section(cls)}
{render_mdx_methods_section(cls)}
"""


def render_mdx_page_title(cls: PyClass, icon: str | None = None) -> str:
    """Renders the MDX for the page title"""
    page_desc = cls.docstring.text if hasattr(cls, "docstring") and hasattr(cls.docstring, "text") else ""

    return f"""---
title: "{cls.name}"
sidebarTitle: "{cls.name}"
icon: "{icon if icon else ""}"
description: "{sanitize_mdx_mintlify_desscription(page_desc)}"
---
"""


def render_mdx_inheritence_section(cls: PyClass, codebase: Codebase) -> str:
    """Renders the MDX for the inheritence section"""
    # Filter on parents who we have docs for
    all_classes_to_document = get_all_classes_to_document(codebase)
    parents = cls.superclasses()
    parents_to_document = []
    for parent in parents:
        if parent.name in all_classes_to_document.keys():
            parents_to_document.append(parent)
    if len(parents_to_document) <= 0:
        return ""
    parents_string = ", ".join([f"[{parent.name}](/{get_mdx_route_for_class(parent)})" for parent in parents_to_document])
    return f"""### Inherits from
{parents_string}
"""


def render_mdx_attributes_section(cls: PyClass) -> str:
    """Renders the MDX for the attributes section"""
    filtered_attributes = cls.attributes(private=False, max_depth=None)
    # filter for only properties
    filtered_attributes = [attribute for attribute in filtered_attributes if attribute.docstring(cls) is not None]
    sorted_attributes = sorted(filtered_attributes, key=lambda x: x.name)
    if len(sorted_attributes) <= 0:
        return ""
    attributes_mdx_string = "\n".join([render_mdx_for_attribute(attribute, cls) for attribute in sorted_attributes])

    return f"""## Attributes
---
{attributes_mdx_string}
"""


def render_mdx_properties_section(cls: PyClass) -> str:
    """Renders the MDX for the properties section"""
    filtered_methods = filter_undocumented_methods_list(cls.methods(private=False, max_depth=None))
    # filter for only properties
    filtered_methods = [method for method in filtered_methods if is_property(method)]
    sorted_methods = sorted(filtered_methods, key=lambda x: x.name)
    if len(sorted_methods) <= 0:
        return ""
    properties_mdx_string = "\n".join([render_mdx_for_property(property, cls) for property in sorted_methods])

    return f"""## Properties
---
{properties_mdx_string}
"""


def render_mdx_methods_section(cls: PyClass) -> str:
    """Renders the MDX for the methods section"""
    filtered_methods = filter_undocumented_methods_list(cls.methods(private=False, max_depth=None))
    # filter properties out of here
    filtered_methods = [method for method in filtered_methods if not is_property(method)]
    sorted_methods = sorted(filtered_methods, key=lambda x: x.name)
    if len(sorted_methods) <= 0:
        return ""
    methods_mdx_string = "\n".join([render_mdx_for_method(method, cls) for method in sorted_methods])

    return f"""## Methods
---
{methods_mdx_string}
"""


def sanitize_docstring_for_markdown(docstring: str) -> str:
    """Sanitize the docstring for MDX"""
    docstring_lines = docstring.splitlines()
    if len(docstring_lines) > 1:
        docstring_lines[1:] = [textwrap.dedent(line) for line in docstring_lines[1:]]
    docstring = "\n".join(docstring_lines)
    if docstring.startswith('"""'):
        docstring = docstring[3:]
    if docstring.endswith('"""'):
        docstring = docstring[:-3]
    return docstring


def render_mdx_for_attribute(attribute: PyAttribute, cls: PyClass) -> str:
    """Renders the MDX for a single property"""
    attribute_docstring = attribute.docstring(cls)
    attribute_docstring = sanitize_docstring_for_markdown(attribute_docstring)

    return f"""### `{attribute.name}`
{attribute_docstring}

```python
{attribute.attribute_docstring}
```

""".strip()


def render_mdx_for_property(property: PyFunction, cls: PyClass) -> str:
    """Renders the MDX for a single property"""
    property_docstring = property.docstring.source if hasattr(property, "docstring") and hasattr(property.docstring, "source") else ""
    if property_docstring == "":
        property_docstring = get_nearest_parent_docstring(property, cls)
    property_docstring = sanitize_docstring_for_markdown(property_docstring)

    return f"""### `{property.name}`
{property_docstring}

```python
{property.function_signature}
    ...
```

""".strip()


########################################################################################################################
# METHODS
########################################################################################################################


def format_parameter_for_mdx(parameter: PyParameter) -> str:
    return f"""
<ParamField path="{parameter.name}" type="{parameter.type}">
</ParamField>""".strip()


def format_parameters_for_mdx(parameters: list[PyParameter]) -> str:
    params = [x for x in parameters if not (x.name.startswith("_") or x.name == "self")]
    return "\n".join([format_parameter_for_mdx(parameter) for parameter in params])


def render_mdx_for_method(method: PyFunction, cls: PyClass) -> str:
    method_docstring = method.docstring.source if hasattr(method, "docstring") and hasattr(method.docstring, "source") else ""

    if method_docstring == "":
        method_docstring = get_nearest_parent_docstring(method, cls)

    method_docstring = sanitize_docstring_for_markdown(method_docstring)

    # =====[ RENDER ]=====
    # TODO add links here
    # TODO add inheritence info here
    mdx_string = f"""### `{method.name}`
{method_docstring}
```python
{method.function_signature}
    ...
```
"""

    return mdx_string


def get_mdx_route_for_class(cls: PyClass) -> str:
    """Get the expected MDX route for a class
    split by /core, /python, and /typescript
    """
    lower_class_name = cls.name.lower()
    if lower_class_name.startswith("py"):
        return f"codebase-sdk/python/{cls.name}"
    elif lower_class_name.startswith(("ts", "jsx")):
        return f"codebase-sdk/typescript/{cls.name}"
    else:
        return f"codebase-sdk/core/{cls.name}"
