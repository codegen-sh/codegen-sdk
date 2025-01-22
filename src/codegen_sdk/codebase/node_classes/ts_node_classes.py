from tree_sitter import Node as TSNode

from codegen_sdk.codebase.node_classes.node_classes import NodeClasses
from codegen_sdk.core.detached_symbols.function_call import FunctionCall
from codegen_sdk.core.expressions.await_expression import AwaitExpression
from codegen_sdk.core.expressions.binary_expression import BinaryExpression
from codegen_sdk.core.expressions.boolean import Boolean
from codegen_sdk.core.expressions.defined_name import DefinedName
from codegen_sdk.core.expressions.name import Name
from codegen_sdk.core.expressions.none_type import NoneType
from codegen_sdk.core.expressions.number import Number
from codegen_sdk.core.expressions.parenthesized_expression import ParenthesizedExpression
from codegen_sdk.core.expressions.subscript_expression import SubscriptExpression
from codegen_sdk.core.expressions.tuple_type import TupleType
from codegen_sdk.core.expressions.unary_expression import UnaryExpression
from codegen_sdk.core.expressions.unpack import Unpack
from codegen_sdk.core.expressions.value import Value
from codegen_sdk.core.statements.comment import Comment
from codegen_sdk.core.symbol_groups.list import List
from codegen_sdk.core.symbol_groups.type_parameters import TypeParameters
from codegen_sdk.typescript.class_definition import TSClass
from codegen_sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen_sdk.typescript.detached_symbols.jsx.element import JSXElement
from codegen_sdk.typescript.detached_symbols.jsx.expression import JSXExpression
from codegen_sdk.typescript.detached_symbols.parameter import TSParameter
from codegen_sdk.typescript.enum_definition import TSEnum
from codegen_sdk.typescript.enums import TSFunctionTypeNames
from codegen_sdk.typescript.expressions.array_type import TSArrayType
from codegen_sdk.typescript.expressions.chained_attribute import TSChainedAttribute
from codegen_sdk.typescript.expressions.conditional_type import TSConditionalType
from codegen_sdk.typescript.expressions.function_type import TSFunctionType
from codegen_sdk.typescript.expressions.generic_type import TSGenericType
from codegen_sdk.typescript.expressions.lookup_type import TSLookupType
from codegen_sdk.typescript.expressions.named_type import TSNamedType
from codegen_sdk.typescript.expressions.object_type import TSObjectType
from codegen_sdk.typescript.expressions.query_type import TSQueryType
from codegen_sdk.typescript.expressions.readonly_type import TSReadonlyType
from codegen_sdk.typescript.expressions.string import TSString
from codegen_sdk.typescript.expressions.ternary_expression import TSTernaryExpression
from codegen_sdk.typescript.expressions.undefined_type import TSUndefinedType
from codegen_sdk.typescript.expressions.union_type import TSUnionType
from codegen_sdk.typescript.file import TSFile
from codegen_sdk.typescript.function import TSFunction
from codegen_sdk.typescript.import_resolution import TSImport
from codegen_sdk.typescript.interface import TSInterface
from codegen_sdk.typescript.namespace import TSNamespace
from codegen_sdk.typescript.statements.comment import TSComment
from codegen_sdk.typescript.statements.import_statement import TSImportStatement
from codegen_sdk.typescript.symbol_groups.dict import TSDict
from codegen_sdk.typescript.type_alias import TSTypeAlias


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
