from typing import TYPE_CHECKING, TypeVar

from src.codegen.sdk.codebase.codebase_graph import CodebaseGraph
from src.codegen.sdk.core.node_id_factory import NodeId
from tree_sitter import Node as TSNode

from codegen.sdk.core.expressions.ternary_expression import TernaryExpression
from codegen.shared.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    from codegen.sdk.core.interfaces.editable import Editable

Parent = TypeVar("Parent", bound="Editable")


@ts_apidoc
class TSTernaryExpression(TernaryExpression[Parent]):
    """Any ternary expression in the code where a condition will determine branched execution."""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent=parent)
        self.condition = self.child_by_field_name("condition")
        self.consequence = self.child_by_field_name("consequence")
        self.alternative = self.child_by_field_name("alternative")
