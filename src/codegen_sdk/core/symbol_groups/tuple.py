from typing import TYPE_CHECKING, TypeVar

from tree_sitter import Node as TSNode

from codegen_sdk.core.expressions.builtin import Builtin
from codegen_sdk.core.expressions.expression import Expression
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.symbol_groups.collection import Collection
from codegen_sdk.writer_decorators import apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph
Parent = TypeVar("Parent", bound=Editable)


@apidoc
class Tuple(Collection["Expression[Self, None]", Parent], Expression[Parent], Builtin):
    """A tuple object.

    You can use standard operations to operate on this list (IE len, del, append, insert, etc)
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self._init_children([self._parse_expression(child) for child in ts_node.named_children if child.type])
