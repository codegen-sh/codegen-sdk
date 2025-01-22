from typing import Generic, TypeVar

from tree_sitter import Node as TSNode

from codegen_sdk.codebase.codebase_graph import CodebaseGraph
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.typescript.expressions.named_type import TSNamedType
from codegen_sdk.writer_decorators import ts_apidoc

Parent = TypeVar("Parent", bound="Editable")


@ts_apidoc
class TSExpressionType(TSNamedType, Generic[Parent]):
    """Type defined by evaluation of an expression

    Attributes:
        expression: The expression to evaluate that yields the type
    """

    expression: Expression["TSExpressionType[Parent]"]

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent)
        self.expression = self._parse_expression(ts_node)
