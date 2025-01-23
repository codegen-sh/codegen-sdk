import json
from typing import Any

from loguru import logger
from tqdm import tqdm

from graph_sitter.code_generation.doc_utils.parse_docstring import parse_docstring
from graph_sitter.code_generation.doc_utils.schemas import ClassDoc, GSDocs, MethodDoc
from graph_sitter.code_generation.doc_utils.utils import IGNORED_ATTRIBUTES, create_path, get_langauge, get_type, get_type_str, has_documentation, is_settter, replace_multiple_types
from graph_sitter.code_generation.graph_sitter_codebase import get_graph_sitter_codebase
from graph_sitter.core.class_definition import Class
from graph_sitter.core.codebase import Codebase

ATTRIBUTES_TO_IGNORE = ["G", "node_id"]


def generate_docs_json(codebase: Codebase, head_commit: str) -> dict[str, dict[str, Any]]:
    """Update documentation table for classes, methods and attributes in the codebase.

    Args:
        codebase (Codebase): the codebase to update the docs for
        head_commit (str): the head commit hash
    Returns:
        dict[str, dict[str, Any]]: the documentation for the codebase
    """
    graph_sitter_docs = GSDocs(classes=[])
    docstring_cache = {}
    types_cache = {}
    attr_cache = {}

    def update_class_doc(cls):
        """Update or create documentation for a class."""
        description = cls.docstring.source.strip('"""') if cls.docstring else None
        parent_classes = [f"<{create_path(parent)}>" for parent in cls.superclasses if isinstance(parent, Class) and has_documentation(parent)]

        cls_doc = ClassDoc(title=cls.name, description=description, content=" ", path=create_path(cls), inherits_from=parent_classes, language=get_langauge(cls), version=str(head_commit))

        return cls_doc

    def process_method(method, cls, cls_doc, seen_methods):
        """Process a single method and update its documentation."""
        if any(dec.name == "noapidoc" for dec in method.decorators):
            return

        if method.name in seen_methods and not is_settter(method):
            return

        if not method.docstring:
            logger.info(f"Method {cls.name}.{method.name} does not have a docstring")
            return

        method_path = create_path(method, cls)
        original_method_path = create_path(method)
        parameters = []
        # Parse docstring only if not cached
        if original_method_path not in docstring_cache:
            parsed = parse_docstring(method.docstring.source)
            if parsed is None:
                raise ValueError(f"Method {cls.name}.{method.name} does not have a docstring")

            # Update parameter types
            for param, parsed_param in zip(method.parameters[1:], parsed["arguments"]):
                if param.name == parsed_param.name:
                    parsed_param.type = replace_multiple_types(
                        codebase=codebase, input_str=parsed_param.type, resolved_types=param.type.resolved_types, parent_class=cls, parent_symbol=method, types_cache=types_cache
                    )
                    if param.default:
                        parsed_param.default = param.default

                    parameters.append(parsed_param)
            # Update return type
            from graph_sitter.python.placeholder.placeholder_return_type import PyReturnTypePlaceholder

            if not isinstance(method.return_type, PyReturnTypePlaceholder):
                return_type = replace_multiple_types(
                    codebase=codebase, input_str=method.return_type.source, resolved_types=method.return_type.resolved_types, parent_class=cls, parent_symbol=method, types_cache=types_cache
                )
            else:
                return_type = None
            parsed["return_types"] = [return_type]

            docstring_cache[original_method_path] = parsed

        parsed_docstring = docstring_cache[original_method_path]
        meta_data = {"parent": create_path(method.parent_class), "path": method.file.filepath}
        method_doc = MethodDoc(
            name=method.name,
            description=parsed_docstring["description"],
            parameters=parsed_docstring["arguments"],
            return_type=parsed_docstring["return_types"],
            return_description=parsed_docstring["return_description"],
            method_type=get_type(method),
            code=method.function_signature,
            path=method_path,
            raises=parsed_docstring["raises"],
            metainfo=meta_data,
            version=str(head_commit),
        )

    def process_attribute(attr, cls, cls_doc, seen_methods):
        """Process a single attribute and update its documentation."""
        if attr.name in seen_methods or attr.name in IGNORED_ATTRIBUTES:
            return

        attr_path = create_path(attr, cls)
        original_attr_path = create_path(attr)

        if original_attr_path not in attr_cache:
            description = attr.docstring(cls)
            attr_return_type = []
            if r_type := get_type_str(attr):
                r_type_source = replace_multiple_types(codebase=codebase, input_str=r_type.source, resolved_types=r_type.resolved_types, parent_class=cls, parent_symbol=attr, types_cache=types_cache)
                attr_return_type.append(r_type_source)

            attr_cache[original_attr_path] = {"description": description, "attr_return_type": attr_return_type}

        attr_info = attr_cache[original_attr_path]
        meta_data = {"parent": create_path(attr.parent_class), "path": attr.file.filepath}

        return MethodDoc(
            name=attr.name,
            description=attr_info["description"],
            parameters=[],
            return_type=attr_info["attr_return_type"],
            return_description=None,
            method_type="attribute",
            code=attr.attribute_docstring,
            path=attr_path,
            raises=[],
            metainfo=meta_data,
            version=str(head_commit),
        )

    # Process all documented classes
    documented_classes = [cls for cls in codebase.classes if has_documentation(cls)]

    for cls in tqdm(documented_classes):
        try:
            cls_doc = update_class_doc(cls)
            graph_sitter_docs.classes.append(cls_doc)
            seen_methods = set()

            # Process methods
            for method in cls.methods(max_depth=None, private=False, magic=False):
                try:
                    method_doc = process_method(method, cls, cls_doc, seen_methods)
                    if not method_doc:
                        continue
                    seen_methods.add(method_doc.name)
                    cls_doc.methods.append(method_doc)
                except Exception as e:
                    logger.info(f"Failed to parse method: {method} - {e}")

            # Process attributes
            for attr in cls.attributes(max_depth=None, private=False):
                if attr.name in ATTRIBUTES_TO_IGNORE:
                    continue
                try:
                    attr_doc = process_attribute(attr, cls, cls_doc, seen_methods)
                    if not attr_doc:
                        continue
                    seen_methods.add(attr_doc.name)
                    cls_doc.attributes.append(attr_doc)
                except Exception as e:
                    logger.info(f"Failed to parse attribute: {attr} - {e}")

        except Exception as e:
            logger.error(f"Error processing class {cls.name}: {e}")
            continue

    return graph_sitter_docs


if __name__ == "__main__":
    codebase = get_graph_sitter_codebase()
    docs = generate_docs_json(codebase, "HEAD")
    with open("/Users/jesusmeza/Documents/graph-sitter/src/graph_sitter/code_generation/docs.json", "w") as f:
        json.dump(docs.model_dump(), f, indent=4)
