import re
from copy import deepcopy

from codegen.sdk.code_generation.enums import DocumentationDecorators
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.core.function import Function
from codegen.sdk.core.symbol import Symbol
from codegen.sdk.enums import NodeType, ProgrammingLanguage
from codegen.sdk.python.class_definition import PyClass
from codegen.sdk.python.function import PyFunction


def get_api_classes_by_decorator(
    codebase: Codebase,
    language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
    docs: bool = True,
) -> dict[str, PyClass]:
    """Returns all classes in a directory that have a specific decorator."""
    classes = {}
    language_specific_decorator = get_decorator_for_language(language).value
    general_decorator = DocumentationDecorators.GENERAL_API.value
    # get language specific classes
    for cls in codebase.classes:
        class_decorators = [decorator.name for decorator in cls.decorators]
        if language_specific_decorator in class_decorators:
            classes[cls.name] = cls
    for cls in codebase.classes:
        class_decorators = [decorator.name for decorator in cls.decorators]
        if general_decorator in class_decorators and cls.name not in classes.keys():
            classes[cls.name] = cls
    return classes


def get_all_classes_to_document(codebase: Codebase) -> dict[str, PyClass]:
    """Returns all classes in a directory that have a specific decorator."""
    python_classes = get_api_classes_by_decorator(codebase=codebase, language=ProgrammingLanguage.PYTHON)
    typescript_classes = get_api_classes_by_decorator(codebase=codebase, language=ProgrammingLanguage.TYPESCRIPT)
    classes = {**typescript_classes, **python_classes}  # Python values will overwrite TypeScript values in case of collision
    return classes


def get_nearest_parent_docstring(method: PyFunction, cls: PyClass) -> str:
    """Returns the PyFunction of the first parent who has a docstring for it"""
    for parent in cls.superclasses():
        if not isinstance(parent, Symbol):
            continue
        for _method in parent.methods():
            if _method.name == method.name:
                if hasattr(_method, "docstring") and hasattr(_method.docstring, "text") and _method.docstring.text != "":
                    return _method.docstring.source
    return ""


def get_language_specific_classes(codebase: Codebase, language: ProgrammingLanguage) -> dict[str, PyClass]:
    classes = {}
    for cls in codebase.classes:
        if cls.get_attribute("language"):
            if cls.get_attribute("language").assignment.value.source.split(".")[1] == language.value:
                classes[cls.name] = cls
    return classes


def get_codemod_classes(codebase: Codebase, language: ProgrammingLanguage) -> dict[str, PyClass]:
    classes = {}
    target_decorator = DocumentationDecorators.CODEMOD.value
    for cls in codebase.classes:
        if target_decorator in [decorator.name for decorator in cls.decorators]:
            if cls.get_attribute("language"):
                if cls.get_attribute("language").assignment.value.source.split(".")[1] == language.value:
                    classes[cls.name] = cls
    return classes


def is_property(method: PyFunction) -> bool:
    """Returns True if the method is a property (denoted by @property decorator)"""
    return method.is_property


def get_parent(cls: PyClass) -> str | None:
    parents = [parent for parent in cls.parent_class_names if parent.source in cls.name]
    if len(parents) > 1:
        raise ValueError(f"More than one parent found for {cls.name}")
    if len(parents) == 0:
        return
    return parents[0].source


def sanitize_mdx_mintlify_desscription(content: str) -> str:
    """Mintlify description field needs to have string escaped, which content doesn't need.
    the must be parsing the description differently or something
    """
    # make sure all `< />` components are properly escaped with a `` inline-block
    # if the string already has the single-quote then this is a no-op
    content = re.sub(r"(?<!`)(<[^>]+>)(?!`)", r"`\1`", content)

    # escape double quote characters
    if re.search(r'\\"', content):
        return content  # No-op if already escaped
    return re.sub(r'(")', r"\\\1", content)


def filter_undocumented_methods_list(doc_methods: list[Function]) -> list[Function]:
    """Returns a list of methods for a given class that should be documented."""
    filtered_doc_methods = [m for m in doc_methods if not m.name.startswith("_")]
    filtered_doc_methods = [m for m in filtered_doc_methods if not any("noapidoc" in d.name for d in m.decorators)]
    return filtered_doc_methods


def get_graph_sitter_class_docstring(cls: PyClass, codebase: Codebase) -> str:
    """Get the documentation for a single GraphSitter class and its methods."""
    # =====[ Parent classes ]=====
    parent_classes = cls.parent_class_names
    parent_class_names = [parent.source for parent in parent_classes if parent.source not in ("Generic", "ABC", "Expression")]
    superclasses = ", ".join([name for name in parent_class_names])
    if len(superclasses) > 0:
        superclasses = f"({superclasses})"

    # =====[ Name + docstring ]=====
    source = f"class {cls.name}{superclasses}:"
    if cls.docstring is not None:
        source += set_indent(string=f'\n"""{cls.docstring.text}"""', indent=1)
    source += "\n"

    # =====[ Attributes ]=====
    if cls.is_subclass_of("Enum"):
        for attribute in cls.attributes:
            source += set_indent(f"\n{attribute.source}", 1)
    else:
        for attribute in cls.attributes(private=False, max_depth=None):
            # Only document attributes which have docstrings
            if docstring := attribute.docstring(cls):
                source += set_indent(f"\n{attribute.attribute_docstring}", 1)
                source += set_indent(string=f'\n"""{docstring}"""', indent=2)
                source += set_indent("\n...\n", 2)

    # =====[ Get inherited method ]=====
    def get_inherited_method(superclasses, method):
        """Returns True if the method is inherited"""
        for s in superclasses:
            for m in s.methods:
                if m.name == method.name:
                    if m.docstring == method.docstring or method.docstring is None:
                        return m
        return None

    # =====[ Get superclasses ]=====
    superclasses = cls.superclasses
    superclasses = list({s.name: s for s in superclasses}.values())
    superclasses = [x for x in superclasses if x.node_type != NodeType.EXTERNAL]

    # TODO use new filter_methods_list function here
    # =====[ Get methods to be documented ]=====
    doc_methods = cls.methods
    doc_methods = [m for m in doc_methods if not m.name.startswith("_")]
    doc_methods = [m for m in doc_methods if not any("noapidoc" in d.name for d in m.decorators)]
    doc_methods = [m for m in doc_methods if get_inherited_method(superclasses, m) is None]

    # =====[ Methods ]=====
    for method in doc_methods:
        if "property" in [decorator.name for decorator in method.decorators]:
            source += set_indent(f"\n@property\n{method.function_signature}", 1)
        else:
            source += set_indent(f"\n{method.function_signature}", 1)
        if method.docstring is not None:
            source += set_indent(string=f'\n"""{method.docstring.text}"""', indent=2)
        source += set_indent("\n...\n", 2)

    # =====[ Format markdown ]=====
    return f"""### {cls.name}\n\n{format_python_codeblock(source)}"""


def remove_first_indent(text):
    lines = text.split("\n")
    first_line = lines[0]
    rest = "\n".join(lines[1:])
    set_indent(rest, 1)
    return first_line + "\n" + rest


def format_python_codeblock(source: str) -> str:
    """A python codeblock in markdown format."""
    # USE 4 backticks instead of 3 so backticks inside the codeblock are handled properly
    cb = f"````python\n{source}\n````"
    return cb


def set_indent(string: str, indent: int) -> str:
    """Sets the indentation of a string."""
    tab = "\t"
    return "\n".join([f"{tab * indent}{line}" for line in string.split("\n")])


def sort_docstrings(docstrings: dict[str, str], preferred_order: list[str]) -> list[str]:
    """Sorts docstrings to a preferred order, putting un-referenced ones last."""
    docstrings = deepcopy(docstrings)
    # ======[ Sort docstrings ]=====
    # Puts un-referenced docstrings last
    sorted_docstrings = []
    for class_name in preferred_order:
        if class_name in docstrings:
            sorted_docstrings.append(docstrings[class_name])
            del docstrings[class_name]
    for class_name in docstrings:
        sorted_docstrings.append(docstrings[class_name])
    return sorted_docstrings


def get_decorator_for_language(
    language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
) -> DocumentationDecorators:
    if language == ProgrammingLanguage.PYTHON:
        return DocumentationDecorators.PYTHON
    elif language == ProgrammingLanguage.TYPESCRIPT:
        return DocumentationDecorators.TYPESCRIPT
