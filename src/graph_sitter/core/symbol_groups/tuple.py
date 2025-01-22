from typing import TYPE_CHECKING, TypeVar

from tree_sitter import Node as TSNode

from graph_sitter.core.expressions.builtin import Builtin
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.symbol_groups.collection import Collection
from graph_sitter.writer_decorators import apidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph
Parent = TypeVar("Parent", bound=Editable)


@apidoc
class Tuple(Collection["Expression[Self, None]", Parent], Expression[Parent], Builtin):
    """A tuple object.

    You can use standard operations to operate on this list (IE len, del, append, insert, etc)
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self._init_children([self._parse_expression(child) for child in ts_node.named_children if child.type])
