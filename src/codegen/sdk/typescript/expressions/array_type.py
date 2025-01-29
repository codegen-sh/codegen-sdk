from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from codegen.sdk.typescript.expressions.named_type import TSNamedType
from codegen.shared.decorators.docs import ts_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

Parent = TypeVar("Parent")


@ts_apidoc
class TSArrayType(TSNamedType[Parent]):
    """Array type
    Examples:
        string[].
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node.named_children[0]
