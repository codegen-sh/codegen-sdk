from typing import TYPE_CHECKING, TypeVar

from tree_sitter import Node as TSNode

from codegen.sdk.core.expressions.named_type import NamedType
from codegen.sdk.writer_decorators import ts_apidoc

if TYPE_CHECKING:
    pass
Parent = TypeVar("Parent")


@ts_apidoc
class TSNamedType(NamedType[Parent]):
    """Named type
    Examples:
        string
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node
