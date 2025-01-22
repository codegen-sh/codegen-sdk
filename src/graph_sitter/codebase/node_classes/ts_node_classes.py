from tree_sitter import Node as TSNode

from graph_sitter.codebase.node_classes.node_classes import NodeClasses
from graph_sitter.core.detached_symbols.function_call import FunctionCall
from graph_sitter.core.expressions.await_expression import AwaitExpression
from graph_sitter.core.expressions.binary_expression import BinaryExpression
from graph_sitter.core.expressions.boolean import Boolean
from graph_sitter.core.expressions.defined_name import DefinedName
from graph_sitter.core.expressions.name import Name
from graph_sitter.core.expressions.none_type import NoneType
from graph_sitter.core.expressions.number import Number
from graph_sitter.core.expressions.parenthesized_expression import ParenthesizedExpression
from graph_sitter.core.expressions.subscript_expression import SubscriptExpression
from graph_sitter.core.expressions.tuple_type import TupleType
from graph_sitter.core.expressions.unary_expression import UnaryExpression
from graph_sitter.core.expressions.unpack import Unpack
from graph_sitter.core.expressions.value import Value
from graph_sitter.core.statements.comment import Comment
from graph_sitter.core.symbol_groups.list import List
from graph_sitter.core.symbol_groups.type_parameters import TypeParameters
from graph_sitter.typescript.class_definition import TSClass
from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock
from graph_sitter.typescript.detached_symbols.jsx.element import JSXElement
from graph_sitter.typescript.detached_symbols.jsx.expression import JSXExpression
from graph_sitter.typescript.detached_symbols.parameter import TSParameter
from graph_sitter.typescript.enum_definition import TSEnum
from graph_sitter.typescript.enums import TSFunctionTypeNames
from graph_sitter.typescript.expressions.array_type import TSArrayType
from graph_sitter.typescript.expressions.chained_attribute import TSChainedAttribute
from graph_sitter.typescript.expressions.conditional_type import TSConditionalType
from graph_sitter.typescript.expressions.function_type import TSFunctionType
from graph_sitter.typescript.expressions.generic_type import TSGenericType
from graph_sitter.typescript.expressions.lookup_type import TSLookupType
from graph_sitter.typescript.expressions.named_type import TSNamedType
from graph_sitter.typescript.expressions.object_type import TSObjectType
from graph_sitter.typescript.expressions.query_type import TSQueryType
from graph_sitter.typescript.expressions.readonly_type import TSReadonlyType
from graph_sitter.typescript.expressions.string import TSString
from graph_sitter.typescript.expressions.ternary_expression import TSTernaryExpression
from graph_sitter.typescript.expressions.undefined_type import TSUndefinedType
from graph_sitter.typescript.expressions.union_type import TSUnionType
from graph_sitter.typescript.file import TSFile
from graph_sitter.typescript.function import TSFunction
from graph_sitter.typescript.import_resolution import TSImport
from graph_sitter.typescript.interface import TSInterface
from graph_sitter.typescript.namespace import TSNamespace
from graph_sitter.typescript.statements.comment import TSComment
from graph_sitter.typescript.statements.import_statement import TSImportStatement
from graph_sitter.typescript.symbol_groups.dict import TSDict
from graph_sitter.typescript.type_alias import TSTypeAlias


def parse_dict(node: TSNode, *args):
    if node.prev_named_sibling and node.prev_named_sibling.text.decode("utf-8").endswith("propTypes"):
        return TSObjectType(node, *args)
    return TSDict(node, *args)


def parse_new(node: TSNode, *args):
    if not node.child_by_field_name("arguments"):
        return Value(node, *args)
    return FunctionCall(node, *args)


TSExpressionMap = {
    "string": TSString,
    "template_string": TSString,
    "object": parse_dict,
    "array": List,
    "name": Name,
    "true": Boolean,
    "false": Boolean,
    "number": Number,
    "property_identifier": DefinedName,
    "call_expression": FunctionCall,
    "identifier": Name,
    "type_identifier": Name,  # HACK
    "shorthand_property_identifier_pattern": Name,  # maybe hack??
    "null": NoneType,
    "comment": TSComment,
    "binary_expression": BinaryExpression,
    "member_expression": TSChainedAttribute,
    "method_definition": TSFunction,
    "parenthesized_expression": ParenthesizedExpression,
    "await_expression": AwaitExpression,
    "unary_expression": UnaryExpression,
    "shorthand_property_identifier": Name,
    "ternary_expression": TSTernaryExpression,
    "jsx_expression": JSXExpression,
    "jsx_element": JSXElement,
    "jsx_closing_element": JSXElement,
    "jsx_opening_element": JSXElement,
    "jsx_self_closing_element": JSXElement,
    "spread_element": Unpack,
    "subscript_expression": SubscriptExpression,
    "type_parameters": TypeParameters,
    "array_pattern": List,
    "new_expression": parse_new,
    # "variable_declarator": TSAssignment.from_named_expression,
    # "property_signature": TSAssignment.from_named_expression,
    # "public_field_definition": TSAssignment.from_named_expression,
    # "assignment_expression": TSAssignment.from_assignment,
    # "augmented_assignment_expression": TSAssignment.from_assignment,
}

TSStatementMap = {
    "import_statement": TSImportStatement,
    "import": TSImportStatement,
}

TSSymbolMap = {
    **{function_type.value: TSFunction.from_function_type for function_type in TSFunctionTypeNames},
    "class_declaration": TSClass,
    "abstract_class_declaration": TSClass,
    "interface_declaration": TSInterface,
    "type_alias_declaration": TSTypeAlias,
    "enum_declaration": TSEnum,
    "internal_module": TSNamespace,
}

TSNodeClasses = NodeClasses(
    file_cls=TSFile,
    class_cls=TSClass,
    function_cls=TSFunction,
    import_cls=TSImport,
    parameter_cls=TSParameter,
    code_block_cls=TSCodeBlock,
    function_call_cls=FunctionCall,
    comment_cls=Comment,
    symbol_map=TSSymbolMap,
    expression_map=TSExpressionMap,
    type_map={
        "union_type": TSUnionType,
        "lookup_type": TSLookupType,
        "predefined_type": TSNamedType,
        "identifier": TSNamedType,
        "type_identifier": TSNamedType,
        "object_type": TSObjectType,
        "generic_type": TSGenericType,
        "literal_type": {
            "null": NoneType,
            "undefined": TSUndefinedType,
            "string": TSNamedType,
        },
        "parenthesized_type": {
            "function_type": TSFunctionType,
            "type_query": TSQueryType,
        },
        "nested_type_identifier": TSNamedType,
        "array_type": TSArrayType,
        "member_expression": TSNamedType,  # TODO: parse generics in class extends clause
        "function_type": TSFunctionType,
        "type_query": TSQueryType,
        "readonly_type": TSReadonlyType,
        "intersection_type": TSUnionType,  # TODO: Not accurate, implement this properly
        "type_parameter": TSNamedType,
        "tuple_type": TupleType,
        "conditional_type": TSConditionalType,
    },
    keywords=["export", "default", "let", "const", "static", "async"],
    type_node_type="type_annotation",
    bool_conversion={
        True: "true",
        False: "false",
    },
)
