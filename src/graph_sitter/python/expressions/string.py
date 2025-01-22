from typing import TYPE_CHECKING, Generic, TypeVar

from tree_sitter import Node as TSNode

from graph_sitter.core.expressions import Expression, String
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.writer_decorators import py_apidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


Parent = TypeVar("Parent", bound="Expression")


@py_apidoc
class PyString(String, Generic[Parent]):
    """An abstract representation of a python string."""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent=parent)
        substitutions = [x for x in ts_node.named_children if x.type == "interpolation"]
        self.expressions = [self._parse_expression(x.child_by_field_name("expression")) for x in substitutions]
