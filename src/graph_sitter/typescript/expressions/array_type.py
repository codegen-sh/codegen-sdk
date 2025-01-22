from typing import TYPE_CHECKING, TypeVar

from tree_sitter import Node as TSNode

from graph_sitter.typescript.expressions.named_type import TSNamedType
from graph_sitter.writer_decorators import ts_apidoc

if TYPE_CHECKING:
    pass
Parent = TypeVar("Parent")


@ts_apidoc
class TSArrayType(TSNamedType[Parent]):
    """Array type
    Examples:
        string[]
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node.named_children[0]
